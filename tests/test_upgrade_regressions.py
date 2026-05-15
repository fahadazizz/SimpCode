"""Regression coverage for upgraded SimpCode prompt and orchestration behavior."""
# pyright: reportMissingImports=false

import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from pydantic import BaseModel


def _install_optional_sdk_stubs():
    if "tiktoken" not in sys.modules:
        tiktoken = ModuleType("tiktoken")

        class _Encoding:
            def encode(self, text):
                return [ord(ch) for ch in text]

        tiktoken.encoding_for_model = lambda model: _Encoding()
        tiktoken.get_encoding = lambda name: _Encoding()
        sys.modules["tiktoken"] = tiktoken

    if "anthropic" not in sys.modules:
        anthropic = ModuleType("anthropic")

        class _AnthropicClient:
            def __init__(self, api_key=None):
                self.api_key = api_key
                self.messages = SimpleNamespace(create=lambda **kwargs: SimpleNamespace(
                    usage=SimpleNamespace(input_tokens=0, output_tokens=0),
                    content=[SimpleNamespace(text="{}")],
                ))

        anthropic.Anthropic = _AnthropicClient
        sys.modules["anthropic"] = anthropic

    if "google" not in sys.modules:
        google = ModuleType("google")
        genai = ModuleType("google.genai")
        types_mod = ModuleType("google.genai.types")

        class _Client:
            def __init__(self, api_key=None):
                self.api_key = api_key
                self.models = SimpleNamespace(generate_content=lambda **kwargs: SimpleNamespace(
                    usage_metadata=SimpleNamespace(prompt_token_count=0, candidates_token_count=0),
                    text="{}",
                ))

        class _GenerateContentConfig:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        genai.Client = _Client
        types_mod.GenerateContentConfig = _GenerateContentConfig
        genai.types = types_mod
        google.genai = genai
        sys.modules["google"] = google
        sys.modules["google.genai"] = genai
        sys.modules["google.genai.types"] = types_mod


_install_optional_sdk_stubs()

from simpcode.core.analyzer import ProjectAnalyzer
from simpcode.core.evolution import EvolutionProposals, GetBetter
from simpcode.core.executor import TakeAction
from simpcode.core.generator import DocumentGenerator, SynthesizedDocs, IntelligenceSynthesizer
from simpcode.core.onboarding import ensure_onboarding_artifacts, needs_onboarding
from simpcode.core.modes import ScanScene
from simpcode.core.planner import ArchitectResponse, ContextRequest, Plan, PlanStep, PlanGenerator
from simpcode.core.config import LLMProviderConfig, SimpConfig, global_config
from simpcode.core.llm.client import LLMClient
from simpcode.harness.budgeter import ContextBudgeter, ContextItem
from simpcode.harness.tools import ToolHarness
from simpcode.utils.hashes import calculate_file_hash
from simpcode.core.llm.openai_provider import OpenAICompatibleProvider
from simpcode.cli.shell import SimpShell
from simpcode.core.workflows import SimpWorkflows
from simpcode.core.state import SessionManager, SessionState
from simpcode.wiki.bootstrap import WikiBootstrap
from simpcode.wiki.engine import WikiEngine
from simpcode.wiki.index import IndexEntry, IndexManager
from simpcode.wiki.models import SourceReference, WikiPage, WikiPageMetadata


class DummyLLM:
    def __init__(self, model_id="dummy-model", responses=None):
        self.model_id = model_id
        self.responses = list(responses or [])
        self.prompts = []

    def structured_output(self, prompt, schema, system_instruction):
        self.prompts.append({
            "prompt": prompt,
            "schema": schema,
            "system_instruction": system_instruction,
        })
        if not self.responses:
            raise AssertionError("No structured_output response queued")
        response = self.responses.pop(0)
        if callable(response):
            return response(prompt, schema, system_instruction)
        return response


class DummyWiki:
    def __init__(self, pages=None, stale_pages=None):
        self.pages = pages or {}
        self.stale_pages = set(stale_pages or [])

    def get_page(self, page_id):
        return self.pages.get(page_id)

    def is_page_stale(self, page):
        return page.metadata.id in self.stale_pages


class DummyBudgeter:
    last_call = None

    def __init__(self, model):
        self.model = model

    def assemble(self, mandatory, semantic, targeted):
        DummyBudgeter.last_call = {
            "mandatory": mandatory,
            "semantic": semantic,
            "targeted": targeted,
        }
        parts = [f"MANDATORY:{item.id}" for item in mandatory]
        parts.extend(f"SEMANTIC:{item.id}" for item in semantic)
        parts.extend(f"TARGETED:{item.id}" for item in targeted)
        return "|".join(parts)


class DummyNavigator:
    def __init__(self, llm):
        self.llm = llm
        self.calls = []

    def navigate(self, query, index_content):
        self.calls.append((query, index_content))
        return SimpleNamespace(pages_to_load=[])


class DummySkillLoader:
    def __init__(self, root):
        self.root = root

    def load_all_skills(self):
        return []


class DummySkillSelector:
    def __init__(self, llm):
        self.llm = llm

    def select(self, task, available_skills):
        return []


@pytest.fixture()
def temp_root(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / ".simp" / "wiki").mkdir(parents=True)
    return root


@pytest.fixture()
def patch_wiki_dir(monkeypatch, temp_root):
    wiki_dir = temp_root / ".simp" / "wiki"
    monkeypatch.setattr("simpcode.core.paths.get_wiki_dir", lambda: wiki_dir)
    return wiki_dir


def test_tool_harness_patch_file_accepts_whitespace_variants(temp_root, patch_wiki_dir):
    code_file = temp_root / "calc.py"
    code_file.write_text("def add(a, b):\n    return a + b\n")

    harness = ToolHarness(temp_root, ["calc.py"])
    result = harness.patch_file(
        "calc.py",
        "def add(a,b):\n return a + b",
        "def add(a, b):\n    return a - b\n",
    )

    assert "File patched" in result
    assert code_file.read_text() == "def add(a, b):\n    return a - b\n\n"


def test_tool_harness_run_shell_blocks_dangerous_operators(temp_root, patch_wiki_dir):
    harness = ToolHarness(temp_root, ["calc.py"])
    output = harness.run_shell("printf 'alpha\\nbeta\\n' | grep beta")
    assert "Security Violation: shell operators are prohibited" in output


def test_tool_harness_list_dir_and_read_scope_are_project_wide(temp_root, patch_wiki_dir):
    (temp_root / "src").mkdir(parents=True, exist_ok=True)
    (temp_root / "src" / "app.py").write_text("print('hello')\n")
    (temp_root / "notes.txt").write_text("notes\n")

    harness = ToolHarness(temp_root, ["src/app.py"])

    listing = harness.list_dir(".")
    assert "src/" in listing
    assert "notes.txt" in listing

    read_result = harness.read_file("notes.txt")
    assert "notes" in read_result

    with pytest.raises(PermissionError):
        harness.write_file("notes.txt", "updated")


def test_context_budgeter_emits_warning_and_keeps_mandatory(monkeypatch):
    monkeypatch.setattr(ContextBudgeter, "count_tokens", lambda self, text: len(text))
    budgeter = ContextBudgeter(total_budget=80, model="dummy")

    mandatory = [ContextItem(id="SPEC.md", content="SPEC CONTENT", priority=0)]
    semantic = [ContextItem(id="modules/core.md", content="X" * 120, priority=2)]
    targeted = [ContextItem(id="CODE:src/app.py", content="Y" * 120, priority=3)]

    assembled = budgeter.assemble(mandatory, semantic, targeted)

    assert "MANDATORY: SPEC.md" in assembled
    assert "[SYSTEM WARNING: Context Budget Exceeded" in assembled
    assert "--- modules/core.md ---" not in assembled


def test_context_budgeter_warns_when_mandatory_exceeds_budget(monkeypatch):
    monkeypatch.setattr(ContextBudgeter, "count_tokens", lambda self, text: len(text))
    budgeter = ContextBudgeter(total_budget=10, model="dummy")

    mandatory = [ContextItem(id="SPEC.md", content="X" * 30, priority=0)]
    assembled = budgeter.assemble(mandatory, [], [])

    assert "MANDATORY: SPEC.md" in assembled
    assert "[SYSTEM WARNING: Mandatory context alone exceeds the total budget" in assembled


def test_scan_scene_loads_simp_without_spec_and_skips_stale_pages(monkeypatch, temp_root, patch_wiki_dir):
    (temp_root / "SIMP.md").write_text("SIMP OVERVIEW\n")
    (temp_root / "src").mkdir(parents=True, exist_ok=True)
    (temp_root / "src" / "fresh.py").write_text("print('fresh')\n")

    fresh_metadata = WikiPageMetadata(
        id="modules/fresh",
        type="module",
        sources=[SourceReference(file_path="src/fresh.py", hash="h1", start_line=1, end_line=1)],
        last_updated=1.0,
        title="Fresh",
    )
    stale_metadata = WikiPageMetadata(
        id="modules/stale",
        type="module",
        sources=[SourceReference(file_path="src/stale.py", hash="h2")],
        last_updated=1.0,
        title="Stale",
    )
    fresh_page = WikiPage(metadata=fresh_metadata, content="FRESH PAGE")
    stale_page = WikiPage(metadata=stale_metadata, content="STALE PAGE")
    index_page = WikiPage(
        metadata=WikiPageMetadata(id="index", type="structural", sources=[], last_updated=1.0, title="Index"),
        content="INDEX CONTENT",
    )

    page_map = {
        "index": index_page,
        "modules/fresh": fresh_page,
        "modules/stale": stale_page,
    }

    class FakeNavigator:
        def __init__(self, llm):
            self.llm = llm

        def navigate(self, query, index_content):
            return SimpleNamespace(pages_to_load=["modules/fresh", "modules/stale"])

    class FakeScannerWiki(DummyWiki):
        pass

    fake_wiki = FakeScannerWiki(page_map, stale_pages={"modules/stale"})
    monkeypatch.setattr("simpcode.core.modes.WikiEngine", lambda root: fake_wiki)
    monkeypatch.setattr("simpcode.core.modes.WikiNavigator", FakeNavigator)
    monkeypatch.setattr("simpcode.core.modes.ContextBudgeter", DummyBudgeter)
    monkeypatch.setattr("simpcode.core.modes.SkillLoader", DummySkillLoader)
    monkeypatch.setattr("simpcode.core.modes.SkillSelector", DummySkillSelector)

    llm = DummyLLM()
    scanner = ScanScene(temp_root, llm)
    context = scanner.run("upgrade system")

    assert "MANDATORY:SIMP.md" in context
    assert "MANDATORY:index.md" in context
    assert DummyBudgeter.last_call is not None
    assert [item.id for item in DummyBudgeter.last_call["mandatory"]][:2] == ["SIMP.md", "index.md"]
    assert [item.id for item in DummyBudgeter.last_call["semantic"]] == ["modules/fresh"]
    assert [item.id for item in DummyBudgeter.last_call["targeted"]] == ["CODE: src/fresh.py (1-1)"]


def test_plan_generator_includes_spec_and_requested_supplemental_context(temp_root):
    (temp_root / "SPEC.md").write_text("SPEC REQUIREMENT: support migrations\n")

    supplemental_page = WikiPage(
        metadata=WikiPageMetadata(id="modules/extra", type="module", sources=[], last_updated=1.0),
        content="SUPPLEMENTAL CONTEXT",
    )

    class FakeWiki:
        def get_page(self, page_id):
            if page_id == "modules/extra":
                return supplemental_page
            return None

        def is_page_stale(self, page):
            return False

    scanner = SimpleNamespace(root=temp_root, wiki=FakeWiki())
    plan = Plan(
        task_id="task-1",
        rationale="r",
        steps=[PlanStep(id=1, target="src/app.py", action="edit", rationale="r", verification="pytest")],
        scope_exclusions=[],
        risk_level="low",
    )

    first_response = ArchitectResponse(
        is_plan=False,
        request=ContextRequest(pages_to_load=["modules/extra"], rationale="need more")
    )
    second_response = ArchitectResponse(is_plan=True, plan=plan)
    llm = DummyLLM(responses=[first_response, second_response])

    generator = PlanGenerator(llm, scanner)
    result = generator.generate("make upgrades", "BASE CONTEXT")

    assert result == plan
    assert "SPEC REQUIREMENT: support migrations" in llm.prompts[0]["prompt"]
    assert "SUPPLEMENTAL CONTEXT" in llm.prompts[1]["prompt"]


def test_get_better_includes_spec_and_writes_changes_log(temp_root, patch_wiki_dir):
    (temp_root / "SPEC.md").write_text("SPEC TARGET: reliability improvements\n")

    proposals = EvolutionProposals(
        new_patterns=["Retry with backoff"],
        new_risks=["Timeouts"],
        new_invariants=["Verify after write"],
        change_log_entry="Captured migration pattern",
    )
    llm = DummyLLM(responses=[proposals])

    evolver = GetBetter(temp_root, llm)
    result = evolver.run("upgrade", "TRACE")

    assert result == proposals
    assert "SPEC TARGET: reliability improvements" in llm.prompts[0]["prompt"]


def test_document_generator_writes_simp_and_spec(temp_root):
    generator = DocumentGenerator(temp_root)
    docs = SynthesizedDocs(simp_md="# SIMP\n", spec_md="# SPEC\n")
    generator.write_docs(docs)

    assert (temp_root / "SIMP.md").read_text() == "# SIMP\n"
    assert (temp_root / "SPEC.md").read_text() == "# SPEC\n"


def test_onboarding_helper_creates_missing_docs_and_index(temp_root):
    docs = SynthesizedDocs(simp_md="", spec_md="")
    metadata = SimpleNamespace(
        name="agentic-chatbot",
        root=str(temp_root),
        file_tree=["README.md", "src/app.py", "tests/test_app.py"],
    )

    assert needs_onboarding(temp_root)
    ensure_onboarding_artifacts(temp_root, docs, metadata)

    assert (temp_root / "SIMP.md").exists()
    assert "Owner: User" in (temp_root / "SIMP.md").read_text()
    assert (temp_root / ".simp" / "wiki" / "index.md").exists()
    assert not (temp_root / "SPEC.md").exists()


def test_onboarding_preserves_existing_spec_when_synthesis_is_empty(temp_root):
    spec_path = temp_root / "SPEC.md"
    spec_path.write_text("# Existing SPEC\nKeep me\n")
    docs = SynthesizedDocs(simp_md="", spec_md="")
    metadata = SimpleNamespace(
        name="agentic-chatbot",
        root=str(temp_root),
        file_tree=["README.md", "src/app.py", "tests/test_app.py"],
    )

    ensure_onboarding_artifacts(temp_root, docs, metadata)

    assert spec_path.read_text() == "# Existing SPEC\nKeep me\n"


def test_onboarding_preserves_existing_simp_when_synthesis_is_empty(temp_root):
    simp_path = temp_root / "SIMP.md"
    simp_path.write_text("# Existing SIMP\nKeep me\n")
    docs = SynthesizedDocs(simp_md="", spec_md="")
    metadata = SimpleNamespace(
        name="agentic-chatbot",
        root=str(temp_root),
        file_tree=["README.md", "src/app.py", "tests/test_app.py"],
    )

    ensure_onboarding_artifacts(temp_root, docs, metadata)

    assert simp_path.read_text() == "# Existing SIMP\nKeep me\n"


def test_workflows_update_simp_requires_explicit_command(monkeypatch, temp_root):
    monkeypatch.setattr("simpcode.core.workflows.get_project_root", lambda: temp_root)
    monkeypatch.setattr(
        ProjectAnalyzer,
        "collect_metadata",
        lambda self: SimpleNamespace(
            name="agentic-chatbot",
            root=str(temp_root),
            file_tree=["README.md", "src/app.py"],
            manifests=["pyproject.toml"],
        ),
    )

    draft = SimpleNamespace(simp_md="# SIMP\n\nOwner: User\nExplicit rule: keep it concise.\n")
    monkeypatch.setattr(SimpWorkflows, "_make_llm", lambda self, provider=None, model=None: DummyLLM(responses=[draft]))

    workflow = SimpWorkflows()
    result = workflow.update_simp("Add explicit rule", approval_prompt=lambda _: "y")

    assert "Explicit rule: keep it concise." in result
    assert "Explicit rule: keep it concise." in (temp_root / "SIMP.md").read_text()


def test_workflows_update_simp_can_be_cancelled(monkeypatch, temp_root):
    monkeypatch.setattr("simpcode.core.workflows.get_project_root", lambda: temp_root)
    monkeypatch.setattr(
        ProjectAnalyzer,
        "collect_metadata",
        lambda self: SimpleNamespace(
            name="agentic-chatbot",
            root=str(temp_root),
            file_tree=["README.md", "src/app.py"],
            manifests=["pyproject.toml"],
        ),
    )

    simp_path = temp_root / "SIMP.md"
    simp_path.write_text("# Existing SIMP\nKeep me\n")
    draft = SimpleNamespace(simp_md="# SIMP\n\nOwner: User\nExplicit rule: keep it concise.\n")
    monkeypatch.setattr(SimpWorkflows, "_make_llm", lambda self, provider=None, model=None: DummyLLM(responses=[draft]))

    workflow = SimpWorkflows()
    result = workflow.update_simp("Add explicit rule", approval_prompt=lambda _: "n")

    assert result == "# Existing SIMP\nKeep me\n"
    assert simp_path.read_text() == "# Existing SIMP\nKeep me\n"


def test_workflows_do_persists_interrupt_state(monkeypatch, temp_root):
    monkeypatch.setattr("simpcode.core.workflows.get_project_root", lambda: temp_root)
    monkeypatch.setattr(SimpWorkflows, "_ensure_onboarded", lambda self, root, provider=None, model=None: False)

    class FakeScanner:
        def __init__(self, root, llm):
            self.root = root
            self.llm = llm

        def run(self, task):
            return "CTX"

    class FakePlanner:
        def __init__(self, llm, scanner):
            self.llm = llm
            self.scanner = scanner

        def generate(self, task, context):
            return Plan(
                task_id="pending",
                rationale="r",
                steps=[PlanStep(id=1, target="src/app.py", action="edit", rationale="r", verification="pytest")],
                scope_exclusions=[],
                risk_level="medium",
            )

    class FakePermissions:
        def __init__(self, console):
            self.console = console

        def review_plan(self, plan, prompt_fn=None):
            return True

    class FakeExecutor:
        def __init__(self, root, llm, session_id=None):
            self.root = root
            self.llm = llm
            self.session_id = session_id

        def execute(self, plan, context):
            raise KeyboardInterrupt

    class FakeEvolver:
        def __init__(self, root, llm):
            self.root = root
            self.llm = llm

        def run(self, task, execution_trace):
            raise AssertionError("evolver should not run after interrupt")

    monkeypatch.setattr("simpcode.core.workflows.ScanScene", FakeScanner)
    monkeypatch.setattr("simpcode.core.workflows.PlanGenerator", FakePlanner)
    monkeypatch.setattr("simpcode.core.workflows.PermissionSystem", FakePermissions)
    monkeypatch.setattr("simpcode.core.workflows.TakeAction", FakeExecutor)
    monkeypatch.setattr("simpcode.core.workflows.GetBetter", FakeEvolver)

    workflow = SimpWorkflows()
    session_manager = SessionManager(str(temp_root))
    session_state = SessionState(session_id="sess-interrupt", project_root=str(temp_root))

    result = workflow.do(
        "improve reliability",
        yes=True,
        provider="groq",
        model="demo",
        session_manager=session_manager,
        session_state=session_state,
    )

    assert result.task_id.startswith("task_")

    saved = session_manager.load_session("sess-interrupt")
    assert saved is not None
    assert saved.status == "interrupted"
    assert len(saved.plans_produced) == 1
    assert saved.plans_produced[0].startswith("task_")
    assert any("KeyboardInterrupt" in error for error in saved.errors_encountered)


def test_openai_compatible_structured_output_tolerates_trailing_noise(monkeypatch):
    class DemoSchema(BaseModel):
        value: int

    provider = OpenAICompatibleProvider("demo-model", "demo-key", "https://example.com/v1", "groq")
    monkeypatch.setattr(provider, "chat", lambda messages, system_instruction: '{"value": 7}\n\nextra text that should be ignored')

    result = provider.structured_output("prompt", DemoSchema, "system")
    assert result.value == 7


def test_google_provider_chat_preserves_history(monkeypatch):
    from simpcode.core.llm.google_provider import GoogleProvider

    captured = {}

    class FakeModels:
        def generate_content(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                usage_metadata=SimpleNamespace(prompt_token_count=1, candidates_token_count=2),
                text="ok",
            )

    class FakeClient:
        def __init__(self, api_key=None):
            self.api_key = api_key
            self.models = FakeModels()

    monkeypatch.setattr("simpcode.core.llm.google_provider.genai.Client", FakeClient)

    provider = GoogleProvider("gemini-demo", "demo-key")
    result = provider.chat(
        [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
            {"role": "user", "content": "continue"},
            {"role": "system", "content": "ignore me as content"},
        ],
        "system prompt",
    )

    assert result == "ok"
    assert captured["model"] == "gemini-demo"
    assert captured["config"].system_instruction == "system prompt"
    assert len(captured["contents"]) == 3
    roles = [item.role if hasattr(item, "role") else item["role"] for item in captured["contents"]]
    assert roles == ["user", "model", "user"]


def test_anthropic_provider_chat_preserves_history(monkeypatch):
    from simpcode.core.llm.anthropic_provider import AnthropicProvider

    captured = {}

    class FakeMessages:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                usage=SimpleNamespace(input_tokens=1, output_tokens=2),
                content=[SimpleNamespace(text="ok")],
            )

    class FakeClient:
        def __init__(self, api_key=None):
            self.api_key = api_key
            self.messages = FakeMessages()

    monkeypatch.setattr("simpcode.core.llm.anthropic_provider.anthropic.Anthropic", FakeClient)

    provider = AnthropicProvider("claude-3-5-sonnet", "demo-key")
    result = provider.chat(
        [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
            {"role": "user", "content": "continue"},
            {"role": "system", "content": "ignore me as content"},
        ],
        "system prompt",
    )

    assert result == "ok"
    assert captured["model"] == "claude-3-5-sonnet"
    assert captured["system"] == "system prompt"
    assert len(captured["messages"]) == 3
    roles = [msg["role"] for msg in captured["messages"]]
    assert roles == ["user", "assistant", "user"]
    contents = [msg["content"] for msg in captured["messages"]]
    assert contents == ["hello", "hi", "continue"]


def test_openai_compatible_provider_chat_preserves_history(monkeypatch):
    from simpcode.core.llm.openai_provider import OpenAICompatibleProvider

    captured = {}

    def fake_post(url, headers, json):
        captured.update({"url": url, "headers": headers, "json": json})
        return SimpleNamespace(
            status_code=200,
            json=lambda: {
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 2},
            },
        )

    class FakeClient:
        def __init__(self, timeout=None):
            self.timeout = timeout

        def post(self, url, **kwargs):
            return fake_post(url, kwargs.get("headers"), kwargs.get("json"))

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr("simpcode.core.llm.openai_provider.httpx.Client", FakeClient)

    provider = OpenAICompatibleProvider("gpt-4", "demo-key", "https://api.openai.com/v1", "openai")
    result = provider.chat(
        [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
            {"role": "user", "content": "continue"},
            {"role": "system", "content": "ignore me as content"},
        ],
        "system prompt",
    )

    assert result == "ok"
    assert captured["json"]["model"] == "gpt-4"
    assert len(captured["json"]["messages"]) == 4
    # First message is system instruction
    assert captured["json"]["messages"][0] == {"role": "system", "content": "system prompt"}
    # Then normalized user/assistant messages (system content filtered out)
    roles = [msg["role"] for msg in captured["json"]["messages"][1:]]
    assert roles == ["user", "assistant", "user"]
    contents = [msg["content"] for msg in captured["json"]["messages"][1:]]
    assert contents == ["hello", "hi", "continue"]


def test_workflows_chat_turn_streams_and_persists_full_response(monkeypatch, temp_root):
    monkeypatch.setattr("simpcode.core.workflows.get_project_root", lambda: temp_root)

    class FakeScanner:
        def __init__(self, root, llm):
            self.root = root
            self.llm = llm

        def run(self, user_input):
            return "SCENE CONTEXT"

    class FakeLLM:
        def __init__(self):
            self.stream_calls = []

        def stream_chat(self, messages, system_instruction):
            self.stream_calls.append((messages, system_instruction))
            yield "Hello"
            yield " world"

    monkeypatch.setattr("simpcode.core.workflows.ScanScene", FakeScanner)

    workflow = SimpWorkflows()
    state = SessionState(session_id="sess-chat", project_root=str(temp_root))
    manager = SessionManager(str(temp_root))
    llm = FakeLLM()

    response = workflow.chat_turn(state, manager, llm, "How are you?")

    assert response == "Hello world"
    assert len(state.history) == 2
    assert state.history[1].content == "Hello world"
    assert llm.stream_calls


def test_llm_client_structured_output_retries_with_correction(monkeypatch):
    class DemoSchema(BaseModel):
        value: int

    class FakeProvider:
        def __init__(self):
            self.calls = []

        def structured_output(self, prompt, schema, system_instruction):
            self.calls.append(system_instruction)
            if len(self.calls) == 1:
                raise ValueError("malformed json")
            return schema(value=9)

        def get_token_usage(self):
            return {"input": 11, "output": 22}

    client = LLMClient.__new__(LLMClient)
    client.provider = FakeProvider()
    client.logger = SimpleNamespace(log_usage=lambda *args, **kwargs: None)
    client.model_id = "demo-model"
    client.refresh = lambda *args, **kwargs: None
    client._build_system_instruction = lambda system_instruction, is_structured=False: "BASE SYSTEM"

    result = client.structured_output("prompt", DemoSchema, "system")

    assert result.value == 9
    assert len(client.provider.calls) == 2
    assert "Previous structured response failed" in client.provider.calls[1]


def test_llm_client_uses_saved_ollama_base_url(monkeypatch):
    config = SimpConfig(
        active_provider="ollama",
        providers={
            "ollama": LLMProviderConfig(
                provider="ollama",
                model_id="llama3.1",
                api_key="local",
                base_url="http://ollama.internal:11434/v1",
            )
        },
    )
    monkeypatch.setattr(global_config, "config", config)

    client = LLMClient()

    assert client.provider_name == "ollama"
    assert client.model_id == "llama3.1"
    assert client.base_url == "http://ollama.internal:11434/v1"
    assert client.provider.base_url == "http://ollama.internal:11434/v1"


def test_llm_client_refresh_picks_up_changed_provider_config(monkeypatch):
    first = SimpConfig(
        active_provider="ollama",
        providers={
            "ollama": LLMProviderConfig(
                provider="ollama",
                model_id="model-a",
                api_key="key-a",
                base_url="http://localhost:11434/v1",
            )
        },
    )
    second = SimpConfig(
        active_provider="ollama",
        providers={
            "ollama": LLMProviderConfig(
                provider="ollama",
                model_id="model-b",
                api_key="key-b",
                base_url="http://ollama.changed:11434/v1",
            )
        },
    )

    monkeypatch.setattr(global_config, "config", first)
    client = LLMClient()

    monkeypatch.setattr(global_config, "config", second)
    client.refresh()

    assert client.model_id == "model-b"
    assert client.api_key == "key-b"
    assert client.base_url == "http://ollama.changed:11434/v1"
    assert client.provider.base_url == "http://ollama.changed:11434/v1"


def test_shell_refresh_llm_rebuilds_from_current_session_state(monkeypatch):
    monkeypatch.setattr(
        global_config,
        "config",
        SimpConfig(
            active_provider="groq",
            providers={
                "groq": LLMProviderConfig(
                    provider="groq",
                    model_id="groq-model",
                    api_key="groq-key",
                )
            },
        ),
    )

    shell = SimpShell.__new__(SimpShell)
    shell.state = SimpleNamespace(current_provider="groq", current_model="groq-model")

    client = shell._refresh_llm()
    assert client.provider_name == "groq"
    assert client.model_id == "groq-model"

    shell.state.current_provider = "ollama"
    shell.state.current_model = "ollama-model"
    monkeypatch.setattr(
        global_config,
        "config",
        SimpConfig(
            active_provider="ollama",
            providers={
                "ollama": LLMProviderConfig(
                    provider="ollama",
                    model_id="ollama-model",
                    api_key="local",
                    base_url="http://ollama.example:11434/v1",
                )
            },
        ),
    )

    refreshed = shell._refresh_llm()
    assert refreshed.provider_name == "ollama"
    assert refreshed.model_id == "ollama-model"
    assert refreshed.base_url == "http://ollama.example:11434/v1"


def test_executor_stops_when_step_verification_fails(monkeypatch, temp_root):
    class FakeHarness:
        def __init__(self, root, allowed_files):
            self.root = root
            self.allowed_files = allowed_files
            self.shell_calls = []
            self.writes = []

        def read_file(self, file_path):
            return "file contents"

        def write_file(self, file_path, content):
            self.writes.append((file_path, content))

        def patch_file(self, file_path, old_string, new_string):
            self.writes.append((file_path, new_string))

        def run_shell(self, command):
            self.shell_calls.append(command)
            if command.startswith("flake8"):
                return ""
            return "EXECUTION FAILURE (Code 1):\nverification failed"

    class FakeLLM:
        def __init__(self):
            self.calls = 0

        def structured_output(self, prompt, schema, system_instruction):
            self.calls += 1
            return SimpleNamespace(
                tool="write_file",
                args={"path": "src/app.py", "content": "print('updated')\n"},
                thought="write the file",
                complete=False,
            )

    monkeypatch.setattr("simpcode.core.executor.ToolHarness", FakeHarness)

    fake_llm = FakeLLM()
    executor = TakeAction(temp_root, fake_llm, session_id="sess-test")
    plan = Plan(
        task_id="task-test",
        rationale="test",
        steps=[
            PlanStep(
                id=1,
                target="src/app.py",
                action="edit",
                rationale="update app",
                verification="pytest -q",
            )
        ],
        scope_exclusions=[],
        risk_level="medium",
    )

    trace = executor.execute(plan, "context")

    assert "verification failed" in trace.lower()
    assert fake_llm.calls == 3


def test_executor_aborts_after_three_failures(monkeypatch, temp_root):
    class FakeHarness:
        def __init__(self, root, allowed_files):
            self.root = root
            self.allowed_files = allowed_files

        def read_file(self, file_path):
            return f"Error: File '{file_path}' does not exist."

        def write_file(self, file_path, content):
            return None

        def patch_file(self, file_path, old_string, new_string):
            return "File patched. You MUST run verification next."

    class FakeLLM:
        def __init__(self):
            self.calls = 0
            self.paths = ["missing-1.txt", "missing-2.txt", "missing-3.txt", "missing-4.txt"]

        def structured_output(self, prompt, schema, system_instruction):
            self.calls += 1
            idx = min(self.calls - 1, len(self.paths) - 1)
            return SimpleNamespace(
                tool="read_file",
                args={"file_path": self.paths[idx]},
                thought="try again",
                complete=False,
            )

    monkeypatch.setattr("simpcode.core.executor.ToolHarness", FakeHarness)

    fake_llm = FakeLLM()
    executor = TakeAction(temp_root, fake_llm, session_id="sess-failures")
    plan = Plan(
        task_id="task-test",
        rationale="test",
        steps=[
            PlanStep(
                id=1,
                target="src/app.py",
                action="edit",
                rationale="update app",
                verification="pytest -q",
            )
        ],
        scope_exclusions=[],
        risk_level="medium",
    )

    trace = executor.execute(plan, "context")

    assert fake_llm.calls == 3
    assert trace.lower().count("does not exist") >= 3


def test_wiki_engine_uses_project_root_even_if_global_helper_is_wrong(monkeypatch, temp_root):
    actual_wiki_dir = temp_root / ".simp" / "wiki"
    actual_wiki_dir.mkdir(parents=True, exist_ok=True)
    (actual_wiki_dir / "modules").mkdir(exist_ok=True)
    wrong_wiki_dir = temp_root / "elsewhere" / "wiki"
    monkeypatch.setattr("simpcode.core.paths.get_wiki_dir", lambda: wrong_wiki_dir)

    page = WikiPage(
        metadata=WikiPageMetadata(
            id="modules/app",
            type="module",
            sources=[],
            last_updated=1.0,
            title="App",
        ),
        content="# App\n",
    )
    page.to_file(actual_wiki_dir / "modules/app.md")

    engine = WikiEngine(temp_root)
    loaded = engine.get_page("modules/app")

    assert loaded is not None
    assert loaded.metadata.id == "modules/app"


def test_index_manager_renders_decision_links_cleanly(temp_root):
    wiki_dir = temp_root / ".simp" / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)
    manager = IndexManager(wiki_dir, token_budget=2000)

    manager.update_index(
        modules=[IndexEntry(name="app", type="module", path="modules/app", description="App module")],
        decisions=[IndexEntry(name="decision-1", type="decision", path="decisions/decision-1", description="Keep the API stable")],
        hotspots=["src/app.py"],
    )

    content = (wiki_dir / "index.md").read_text()
    assert "[[decisions/decision-1|decision-1]]" in content
    assert "IndexEntry" not in content


@pytest.mark.parametrize(
    "prompt_name,required_text",
    [
        ("onboarding_documents", "leave spec_md empty"),
        ("wiki_bootstrap", "Generate the BootstrapResult"),
        ("staff_architect_plan", "USER TASK:"),
        ("staff_researcher_learning", "SPEC (Target State, optional):"),
        ("staff_implementer_step", "CURRENT CONTEXT:"),
        ("wiki_navigation", "PROJECT INDEX:"),
        ("skill_selector", "AVAILABLE SKILLS:"),
        ("wiki_cognitive_merge", "CURRENT COGNITIVE LAYER"),
    ],
)
def test_prompt_assets_exist_and_contain_expected_contract(prompt_name, required_text):
    from simpcode.core.prompts import registry

    prompt = registry.load(prompt_name, include_base=False)
    assert required_text in prompt


@pytest.mark.parametrize(
    "mod_name,file_tree,expected",
    [
        ("core", ["core/__init__.py"], "core/__init__.py"),
        ("web", ["src/web/index.ts"], "src/web/index.ts"),
        ("app", ["app/main.rs"], "app/main.rs"),
        ("service", ["service/main.go"], "service/main.go"),
    ],
)
def test_wiki_bootstrap_guess_main_file_supports_multiple_languages(temp_root, mod_name, file_tree, expected):
    bootstrap = WikiBootstrap(DummyLLM(), temp_root)
    assert bootstrap._guess_main_file(mod_name, file_tree) == expected


def test_project_analyzer_compresses_large_file_trees(tmp_path_factory):
    root = tmp_path_factory.mktemp("analyzer")
    deep_dir = root / "src" / "pkg" / "component"
    deep_dir.mkdir(parents=True)
    for idx in range(501):
        (deep_dir / f"file_{idx}.py").write_text("print('x')\n")

    analyzer = ProjectAnalyzer(root)
    metadata = analyzer.collect_metadata()

    assert len(metadata.file_tree) <= 2000
    assert any("src/pkg/component/*" in item for item in metadata.file_tree)

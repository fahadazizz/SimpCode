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
from simpcode.core.generator import DocumentGenerator, SynthesizedDocs, IntelligenceSynthesizer
from simpcode.core.onboarding import ensure_onboarding_artifacts, needs_onboarding
from simpcode.core.modes import ScanScene
from simpcode.core.planner import ArchitectResponse, ContextRequest, Plan, PlanStep, PlanGenerator
from simpcode.harness.budgeter import ContextBudgeter, ContextItem
from simpcode.harness.tools import ToolHarness
from simpcode.utils.hashes import calculate_file_hash
from simpcode.core.llm.openai_provider import OpenAICompatibleProvider
from simpcode.wiki.bootstrap import WikiBootstrap
from simpcode.wiki.engine import WikiEngine
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
    monkeypatch.setattr("simpcode.wiki.engine.get_wiki_dir", lambda: wiki_dir)
    monkeypatch.setattr("simpcode.core.evolution.get_wiki_dir", lambda: wiki_dir)
    return wiki_dir


def test_tool_harness_refreshes_wiki_hash_after_write(temp_root, patch_wiki_dir):
    source_file = temp_root / "app.py"
    source_file.write_text("print('hello')\n")
    initial_hash = calculate_file_hash(str(source_file))

    metadata = WikiPageMetadata(
        id="modules/app",
        type="module",
        sources=[SourceReference(file_path="app.py", hash=initial_hash)],
        last_updated=1.0,
        title="Module: app",
    )
    (patch_wiki_dir / "modules").mkdir(parents=True, exist_ok=True)
    WikiPage(metadata=metadata, content="# app\n").to_file(patch_wiki_dir / "modules/app.md")

    harness = ToolHarness(temp_root, ["app.py"])
    harness.write_file("app.py", "print('updated')\n")

    page = WikiPage.from_file(patch_wiki_dir / "modules/app.md")
    assert page.metadata.sources[0].hash == calculate_file_hash(str(source_file))
    assert page.metadata.sources[0].hash != initial_hash


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


def test_tool_harness_run_shell_supports_pipes(temp_root, patch_wiki_dir):
    harness = ToolHarness(temp_root, ["calc.py"])
    output = harness.run_shell("printf 'alpha\\nbeta\\n' | grep beta")
    assert "beta" in output


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
    assert (patch_wiki_dir / "changes.md").exists()
    assert "Captured migration pattern" in (patch_wiki_dir / "changes.md").read_text()


def test_document_generator_writes_simp_and_spec(temp_root):
    generator = DocumentGenerator(temp_root)
    docs = SynthesizedDocs(simp_md="# SIMP\n", spec_md="")
    generator.write_docs(docs)

    assert (temp_root / "SIMP.md").read_text() == "# SIMP\n"
    assert not (temp_root / "SPEC.md").exists()


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
    assert (temp_root / ".simp" / "wiki" / "index.md").exists()
    assert not (temp_root / "SPEC.md").exists()


def test_openai_compatible_structured_output_tolerates_trailing_noise(monkeypatch):
    class DemoSchema(BaseModel):
        value: int

    provider = OpenAICompatibleProvider("demo-model", "demo-key", "https://example.com/v1", "groq")
    monkeypatch.setattr(provider, "chat", lambda messages, system_instruction: '{"value": 7}\n\nextra text that should be ignored')

    result = provider.structured_output("prompt", DemoSchema, "system")
    assert result.value == 7


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

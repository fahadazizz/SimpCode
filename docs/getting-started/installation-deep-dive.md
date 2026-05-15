# Installation Deep Dive

This page covers installation details, environment setup, and common pitfalls.

## 1. Python and Environment Requirements

SimpCode currently requires Python `>=3.12`.

Recommended setup:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install package:

```bash
pip install -e .
```

Why editable mode:

- easier local development,
- command updates reflect immediately,
- docs and code iteration remain synchronized.

## 2. Dependency Notes

Core runtime dependencies include:

- Click and Rich for CLI/TUI UX
- Pydantic for structured models
- Prompt Toolkit for interactive shell
- provider SDKs and HTTP tooling
- YAML parsing for wiki frontmatter
- `tiktoken` for token budgeting logic

Install through `pip install -e .` using `pyproject.toml` metadata.

## 3. Verifying Installation

Basic checks:

```bash
simp --help
simp setup
```

If command is not found:

- verify virtual environment is active,
- reinstall editable package,
- ensure shell sees venv bin path.

## 4. Provider Setup Deep Details

Run:

```bash
simp setup
```

You will be prompted for:

- provider
- model ID
- API key (except Ollama)
- Ollama base URL when provider is Ollama

Supported setup providers:

- `groq`
- `anthropic`
- `openai`
- `openrouter`
- `google`
- `ollama`

## 5. Where Config Is Stored

ConfigManager attempts writable path in this order:

1. `~/.simpcode/config.json`
2. `<project>/.simp/config.json`

If global path is writable, that is preferred.

## 6. Clean Reinstall Procedure

If environment is broken:

```bash
deactivate || true
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then rerun provider setup:

```bash
simp setup
```

## 7. Optional Local-Only Provider Path

If using local Ollama:

- set provider to `ollama`,
- configure reachable base URL,
- verify Ollama server is running before using ask/do flows.

## 8. Installation Validation Checklist

1. `simp` launches without crashing.
2. `simp setup` writes config.
3. `simp init` enters TUI.
4. `/status` and `/wiki list` execute.
5. `/ask` returns contextual response.

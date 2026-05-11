# Project Overview
The SimpCode project is a spec-driven, semantically aware agentic coding assistant. It utilizes a variety of technologies, including Click, Rich, Pydantic, and Anthropic, to provide a high-integrity engineering experience.

## Core Components
* `src/simpcode/core`: This directory contains the core logic of the project, including the planner, analyzer, generator, and executor.
* `src/simpcode/wiki`: This directory contains the wiki-related components, including the bootstrap, models, and engine.
* `src/simpcode/cli`: This directory contains the command-line interface components, including the main entry point and shell.
* `src/simpcode/harness`: This directory contains the harness-related components, including the permissions and budgeter.

## Dependencies
The project depends on the following libraries:
* Click
* Rich
* Pydantic
* Anthropic
* Google GenAI
* Python Dotenv
* PyYAML
* HTTPX
* Tiktoken
* Prompt Toolkit

## Verification Pipeline
The project uses the following verification pipeline:
* Pytest

## Invariants
* All logic must be in the `src/simpcode/core` directory.
* All wiki-related components must be in the `src/simpcode/wiki` directory.
* All command-line interface components must be in the `src/simpcode/cli` directory.
* All harness-related components must be in the `src/simpcode/harness` directory.
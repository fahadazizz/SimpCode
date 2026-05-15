# Architecture Diagram

This file contains the compact Mermaid diagram summarizing the primary runtime components and their interactions.

```mermaid
flowchart LR
  CLI["CLI / TUI (simp)"] -->|invokes| Shell[SimpShell]
  Shell -->|routes| Planner[PlanGenerator]
  Planner -->|produces plan| Executor[TakeAction / Executor]
  Executor -->|uses| ToolHarness[ToolHarness]
  Executor -->|updates| WikiEngine[Wiki Engine]
  WikiEngine -->|persists| Registry[.simp/wiki/registry.json]
  WikiEngine -->|reads/writes| WikiFS[.simp/wiki/*.md]
  Executor -->|uses| LLM[LLMClient]
  LLM -->|provider| ExternalAPI[Provider (OpenAI/Anthropic/...)]
  Executor -->|logs| ExecLogs[.simp/logs/*.jsonl]
  Shell -->|stores| Sessions[.simp/sessions]
  IndexManager[IndexManager] -.->|reads| WikiFS
  IndexManager -.->|writes| IndexFile[index.md]
  ToolHarness -->|executes sandboxed| Subprocess[Local subprocess]
  subgraph Code
    Planner
    Executor
    WikiEngine
    ToolHarness
    IndexManager
  end
```

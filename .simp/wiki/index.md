---
id: index
type: structural
sources: []
last_updated: 1778454671.2556438
title: Project Index
---

# Project Index

This is the high-level map of the codebase. Navigation should start here.

## Modules
- [[modules/core|core]]: PRIMARY responsibility: Provide the core functionality of SimpCode, including project analysis, intelligence synthesis, and plan generation. Cross-module dependencies: wiki, harness, cli.
- [[modules/wiki|wiki]]: PRIMARY responsibility: Manage the wiki and provide functionality for wiki-related tasks. Cross-module dependencies: core, harness.
- [[modules/harness|harness]]: PRIMARY responsibility: Provide functionality for permissions and budgeting. Cross-module dependencies: core, wiki.
- [[modules/cli|cli]]: PRIMARY responsibility: Provide the command-line interface for SimpCode. Cross-module dependencies: core, wiki, harness.
## Decisions
## Hotspots
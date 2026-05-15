# Concepts Index

This section explains how to think about SimpCode so that command behavior feels predictable instead of magical.

If you understand these concepts, you can safely use SimpCode on production repositories and reason about why it behaves the way it does.

## Concept Groups

- [Architecture Concept](architecture.md): the runtime model from prompt to verified change.

## Concept Summary

### 1. Local-First System

SimpCode is not a cloud workspace orchestrator. It works against your local repository and local artifact state.

### 2. Plan Before Change

Execution is plan-mediated, with explicit user approval unless `--yes` is used.

### 3. Scoped Writes, Broad Reads

Reads are broad (with exclusions), writes are scoped to plan-approved targets.

### 4. Knowledge as Files

Wiki pages are real markdown files with frontmatter metadata and source hash tracking.

### 5. Recovery Through Artifacts

Plans, sessions, logs, and wiki state are persisted under `.simp/`, making behavior inspectable and recoverable.

## Why These Concepts Matter

Most tooling confusion comes from unclear assumptions about ownership and control.

SimpCode intentionally chooses:

- deterministic artifacts over hidden memory,
- explicit approval over silent writes,
- traceability over opaque autonomous behavior.

This does not remove all risk, but it gives you a concrete operational model.

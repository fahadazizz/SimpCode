# Wiki System

The Wiki system is the "memory" of SimpCode. It consists of a structured set of Markdown files that provide a semantic layer over the raw source code.

## Directory Structure
The Wiki is stored in `.simp/wiki/`:
- `index.md`: The root map of the Wiki, used for navigation.
- `*.md`: Individual pages describing modules, patterns, or invariants.

## Core Components

### `WikiEngine`
**Location:** `src/simpcode/wiki/engine.py`
The engine is responsible for reading and writing Wiki pages and performing staleness checks.
- `check_staleness(page)`: Compares the current file hashes on disk with those stored in the page's metadata.
- `get_all_pages()`: Loads all pages from the Wiki directory.

### `WikiNavigator`
**Location:** `src/simpcode/wiki/navigator.py`
The navigator uses an LLM to decide which Wiki pages are relevant to a given task based on the `index.md`.
- `navigate(task, index_content)`: Returns a `NavigationDecision` containing a list of page IDs to load.

## Data Models
**Location:** `src/simpcode/wiki/models.py`
- `WikiPage`: Represents a page with Markdown content and YAML front-matter metadata.
- `SourceReference`: Pinned reference to a file or line range, including a hash for freshness tracking.

## Freshness Management
SimpCode ensures the Wiki remains accurate through:
1.  **Automatic Updates:** The `ToolHarness` updates hashes immediately after a successful `write_file`.
2.  **Manual Sync:** The `simp sync` command performs a batch check across all pages.
3.  **Staleness Awareness:** The `ScanScene` mode can detect stale pages during the research phase.

import os
from pathlib import Path

def get_simp_dir() -> Path:
    """Returns the .simp directory path, ensuring it exists."""
    # In a real tool, this would be relative to the project root.
    # For now, we assume the current working directory is the root.
    root = Path.cwd()
    simp_dir = root / ".simp"
    simp_dir.mkdir(exist_ok=True)
    return simp_dir

def get_wiki_dir() -> Path:
    wiki_dir = get_simp_dir() / "wiki"
    wiki_dir.mkdir(exist_ok=True)
    return wiki_dir

def get_sessions_dir() -> Path:
    sessions_dir = get_simp_dir() / "sessions"
    sessions_dir.mkdir(exist_ok=True)
    return sessions_dir

def get_registry_path() -> Path:
    return get_simp_dir() / "registry.json"

def get_token_log_path() -> Path:
    return get_simp_dir() / "tokens.log"

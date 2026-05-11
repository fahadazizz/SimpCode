import os
from pathlib import Path
from simpcode.utils.paths import PathManager

def get_project_root() -> Path:
    return PathManager.find_project_root()

def get_simp_dir() -> Path:
    """Returns the .simp directory path, ensuring it exists."""
    root = get_project_root()
    simp_dir = root / ".simp"
    simp_dir.mkdir(parents=True, exist_ok=True)
    return simp_dir

def get_wiki_dir() -> Path:
    wiki_dir = get_simp_dir() / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)
    return wiki_dir

def get_sessions_dir() -> Path:
    sessions_dir = get_simp_dir() / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    return sessions_dir

def get_plans_dir() -> Path:
    plans_dir = get_simp_dir() / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    return plans_dir

def get_logs_dir() -> Path:
    logs_dir = get_simp_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir

def get_registry_path() -> Path:
    return get_simp_dir() / "registry.json"

def get_token_log_path() -> Path:
    return get_simp_dir() / "tokens.log"

import hashlib
import os
from pathlib import Path

def calculate_file_hash(file_path: str) -> str:
    """Calculates SHA-256 hash of a complete file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def calculate_range_hash(file_path: str, start_line: int, end_line: int) -> str:
    """
    Calculates SHA-256 hash of a specific line range (inclusive).
    Uses a streaming approach to be memory efficient for large files.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    sha256_hash = hashlib.sha256()
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            current_line = i + 1
            if current_line >= start_line and current_line <= end_line:
                sha256_hash.update(line.encode("utf-8"))
            if current_line > end_line:
                break
        
    return sha256_hash.hexdigest()

def read_range(file_path: str, start_line: int, end_line: int) -> str:
    """
    Reads a specific line range (inclusive, 1-indexed) from a file.
    """
    lines = []
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            current_line = i + 1
            if current_line >= start_line and current_line <= end_line:
                lines.append(line)
            if current_line > end_line:
                break
    return "".join(lines)

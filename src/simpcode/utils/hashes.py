import hashlib
import os

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
    Lines are 1-indexed.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    sha256_hash = hashlib.sha256()
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    # Slice is 0-indexed, start_line is 1-indexed.
    # end_line is inclusive in our spec, so we take up to end_line.
    selected_lines = lines[start_line-1 : end_line]
    
    for line in selected_lines:
        sha256_hash.update(line.encode("utf-8"))
        
    return sha256_hash.hexdigest()

import sys
from pathlib import Path
from simpcode.wiki.engine import WikiEngine
from simpcode.wiki.models import WikiPage, WikiPageMetadata
import time

def main():
    root = Path(".")
    engine = WikiEngine(root)
    
    # Test 1: changes.md creation
    print("Testing append_change_log...")
    engine.append_change_log("Test task", ["test.py"], "Testing rationale")
    page = engine.get_page("changes")
    assert page is not None, "changes.md should be created"
    assert "Testing rationale" in page.content
    print("Test 1 Passed.")

    # Test 2: Index hotspots
    print("Testing update_hotspots...")
    from simpcode.wiki.index import IndexManager, IndexEntry
    idx = IndexManager(engine.wiki_dir)
    # create dummy index
    idx.update_index([IndexEntry(name="a", type="module", path="a", description="a")], [], [])
    
    idx.update_hotspots(["test_hotspot.py"])
    idx_page = engine.get_page("index")
    assert "- test_hotspot.py" in idx_page.content
    print("Test 2 Passed.")
    
    print("All basic unit tests passed!")

if __name__ == "__main__":
    main()

import unittest
import os
import tempfile
import time
from pathlib import Path
from simpcode.wiki.models import WikiPage, WikiPageMetadata, SourceReference
from simpcode.wiki.engine import WikiEngine
from simpcode.utils.hashes import calculate_file_hash

class TestWikiEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.test_dir.name)
        
        # Create a mock code file
        self.code_file = self.root / "app.py"
        self.code_file.write_text("print('hello')")
        self.initial_hash = calculate_file_hash(str(self.code_file))
        
        # Setup .simp/wiki
        self.simp_dir = self.root / ".simp"
        self.wiki_dir = self.simp_dir / "wiki"
        self.wiki_dir.mkdir(parents=True)
        
        # Monkeypatch paths for testing
        import simpcode.core.paths
        self.orig_get_wiki_dir = simpcode.core.paths.get_wiki_dir
        simpcode.core.paths.get_wiki_dir = lambda: self.wiki_dir

    def tearDown(self):
        import simpcode.core.paths
        simpcode.core.paths.get_wiki_dir = self.orig_get_wiki_dir
        self.test_dir.cleanup()

    def test_staleness_detection(self):
        metadata = WikiPageMetadata(
            id="app_module",
            type="module",
            sources=[SourceReference(file_path="app.py", hash=self.initial_hash)],
            last_updated=time.time()
        )
        page = WikiPage(metadata=metadata, content="App module info")
        
        engine = WikiEngine(self.root)
        self.assertFalse(engine.is_page_stale(page))
        
        # Modify the code file
        self.code_file.write_text("print('hello world')")
        self.assertTrue(engine.is_page_stale(page))
        
        stale = engine.check_staleness(page)
        self.assertEqual(len(stale), 1)
        self.assertEqual(stale[0][1], calculate_file_hash(str(self.code_file)))

if __name__ == "__main__":
    unittest.main()

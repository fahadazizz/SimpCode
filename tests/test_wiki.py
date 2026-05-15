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

    # ============ PHASE 2: Integration Tests ============

    def test_wiki_update_with_large_registry(self):
        """Verify wiki update doesn't trigger full page scan with large registry."""
        engine = WikiEngine(self.root)
        
        # Create registry with 1000 pages
        for i in range(1000):
            page = WikiPage(
                metadata=WikiPageMetadata(
                    id=f"page_{i}",
                    type="cognitive",
                    sources=[SourceReference(
                        file_path=f"file_{i}.py",
                        hash=f"hash_{i}"
                    )],
                    last_updated=time.time()
                ),
                content=f"Page {i}"
            )
            engine.save_page(page)
        
        # Now get_pages_for_file should use O(1) registry lookup
        # not scan all 1000 pages
        result = engine.get_pages_for_file("file_500.py")
        self.assertEqual(result, ["page_500"])
        
        # Verify registry has all entries
        registry = engine._load_registry()
        self.assertIn("file_500.py", registry)

    def test_save_page_with_source_changes(self):
        """Verify save_page correctly tracks source changes with _previous_sources."""
        engine = WikiEngine(self.root)
        
        # Initial save with 2 sources
        page = WikiPage(
            metadata=WikiPageMetadata(
                id="test_page",
                type="cognitive",
                sources=[
                    SourceReference(file_path="file1.py", hash="hash1"),
                    SourceReference(file_path="file2.py", hash="hash2"),
                ],
                last_updated=time.time()
            ),
            content="Initial"
        )
        engine.save_page(page)
        
        registry = engine._load_registry()
        self.assertIn("test_page", registry.get("file1.py", []))
        self.assertIn("test_page", registry.get("file2.py", []))
        
        # Modify sources to file2 and file3
        page.metadata.sources = [
            SourceReference(file_path="file2.py", hash="hash2"),
            SourceReference(file_path="file3.py", hash="hash3"),
        ]
        engine.save_page(page)
        
        # Verify registry was updated correctly
        registry = engine._load_registry()
        self.assertNotIn("test_page", registry.get("file1.py", []), 
                         "Old source file1.py not cleaned up")
        self.assertIn("test_page", registry["file2.py"], 
                      "Continuing source file2.py should remain")
        self.assertIn("test_page", registry["file3.py"], 
                      "New source file3.py should be added")

    def test_registry_consistency_across_saves(self):
        """Verify registry remains consistent after multiple save/update cycles."""
        engine = WikiEngine(self.root)
        
        # Create initial pages
        pages = {}
        for i in range(20):
            page = WikiPage(
                metadata=WikiPageMetadata(
                    id=f"page_{i}",
                    type="cognitive",
                    sources=[SourceReference(file_path=f"file_{i}.py", hash=f"hash_{i}")],
                    last_updated=time.time()
                ),
                content=f"Page {i}"
            )
            engine.save_page(page)
            pages[f"page_{i}"] = page
        
        # Update some pages with new sources
        for i in [0, 5, 10, 15]:
            pages[f"page_{i}"].metadata.sources = [
                SourceReference(file_path=f"new_file_{i}.py", hash=f"new_hash_{i}"),
                SourceReference(file_path=f"file_{i}.py", hash=f"hash_{i}"),
            ]
            engine.save_page(pages[f"page_{i}"])
        
        # Verify registry integrity
        registry = engine._load_registry()
        
        # Check that updated pages have correct entries
        for i in [0, 5, 10, 15]:
            self.assertIn(f"page_{i}", registry[f"new_file_{i}.py"])
            self.assertIn(f"page_{i}", registry[f"file_{i}.py"])
        
        # Check that unchanged pages are still correct
        for i in [1, 2, 3, 4, 6, 7, 11, 12, 16, 17]:
            self.assertIn(f"page_{i}", registry[f"file_{i}.py"])
        
        # Verify no orphaned entries
        for file_path, page_ids in registry.items():
            for page_id in page_ids:
                self.assertIn(page_id, pages, f"Orphaned entry: {page_id} in {file_path}")

    def test_get_all_pages_cache_works_correctly(self):
        """Verify get_all_pages cache hits work and invalidates properly."""
        engine = WikiEngine(self.root)
        
        # Create 50 pages
        for i in range(50):
            page = WikiPage(
                metadata=WikiPageMetadata(
                    id=f"page_{i}",
                    type="cognitive",
                    sources=[SourceReference(file_path=f"file_{i}.py", hash=f"hash_{i}")],
                    last_updated=time.time()
                ),
                content=f"Page {i}"
            )
            engine.save_page(page)
        
        # First call - cache miss
        pages1 = engine.get_all_pages()
        self.assertEqual(len(pages1), 50)
        mtime1 = engine._pages_cache_mtime
        self.assertIsNotNone(mtime1)
        
        # Second call - should hit cache (same mtime)
        pages2 = engine.get_all_pages()
        self.assertEqual(len(pages2), 50)
        self.assertEqual(engine._pages_cache_mtime, mtime1)
        
        # Add new page - should invalidate cache
        new_page = WikiPage(
            metadata=WikiPageMetadata(
                id="page_50",
                type="cognitive",
                sources=[SourceReference(file_path="file_50.py", hash="hash_50")],
                last_updated=time.time()
            ),
            content="Page 50"
        )
        engine.save_page(new_page)
        
        # Cache should be invalidated
        self.assertEqual(engine._pages_cache, [])
        self.assertIsNone(engine._pages_cache_mtime)
        
        # Next call should rebuild cache with 51 pages
        pages3 = engine.get_all_pages()
        self.assertEqual(len(pages3), 51)

    # ============ PHASE 2: Regression Tests ============

    def test_wiki_engine_basic_operations_still_work(self):
        """Verify basic wiki operations unchanged by performance fixes."""
        engine = WikiEngine(self.root)
        
        # Test save_page
        page = WikiPage(
            metadata=WikiPageMetadata(
                id="test_page",
                type="module",
                sources=[SourceReference(file_path="app.py", hash="hash123")],
                last_updated=time.time(),
                title="Test Page"
            ),
            content="# Test Page\nContent here"
        )
        engine.save_page(page)
        
        # Test get_page
        loaded = engine.get_page("test_page")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.metadata.id, "test_page")
        self.assertEqual(loaded.metadata.title, "Test Page")
        self.assertIn("Content here", loaded.content)
        
        # Test get_pages_for_file
        pages = engine.get_pages_for_file("app.py")
        self.assertEqual(pages, ["test_page"])
        
        # Test get_all_pages
        all_pages = engine.get_all_pages()
        self.assertEqual(len(all_pages), 1)
        self.assertEqual(all_pages[0].metadata.id, "test_page")

    def test_registry_rebuilds_correctly_on_stale_cache(self):
        """Verify cache invalidation works when registry.json is modified."""
        engine = WikiEngine(self.root)
        
        # Create initial page
        page = WikiPage(
            metadata=WikiPageMetadata(
                id="page_1",
                type="cognitive",
                sources=[SourceReference(file_path="file_1.py", hash="hash_1")],
                last_updated=time.time()
            ),
            content="Page 1"
        )
        engine.save_page(page)
        
        # Load registry to populate cache
        registry = engine._load_registry()
        mtime_before = engine._registry_cache_mtime
        
        # Simulate external modification (touch registry.json)
        time.sleep(0.01)
        engine.registry_path.touch()
        
        # Next load should detect mtime change and reload
        registry_reloaded = engine._load_registry()
        mtime_after = engine._registry_cache_mtime
        
        # mtime should have changed
        self.assertNotEqual(mtime_before, mtime_after)
        self.assertIn("file_1.py", registry_reloaded)

    def test_page_staleness_detection_unchanged(self):
        """Regression: page staleness detection still works after fixes."""
        engine = WikiEngine(self.root)
        
        # Create page with initial hash
        hash_v1 = calculate_file_hash(str(self.code_file))
        metadata = WikiPageMetadata(
            id="app_module",
            type="module",
            sources=[SourceReference(file_path="app.py", hash=hash_v1)],
            last_updated=time.time()
        )
        page = WikiPage(metadata=metadata, content="Version 1")
        
        # Page should not be stale
        self.assertFalse(engine.is_page_stale(page))
        
        # Modify source file
        self.code_file.write_text("print('modified')")
        
        # Page should now be stale
        self.assertTrue(engine.is_page_stale(page))

    def test_multiple_pages_same_source(self):
        """Verify multiple pages can track same source without conflicts."""
        engine = WikiEngine(self.root)
        
        # Create multiple pages tracking same file
        for i in range(5):
            page = WikiPage(
                metadata=WikiPageMetadata(
                    id=f"page_{i}",
                    type="cognitive",
                    sources=[SourceReference(file_path="shared_file.py", hash="shared_hash")],
                    last_updated=time.time()
                ),
                content=f"Page {i} tracking shared file"
            )
            engine.save_page(page)
        
        # All pages should be returned for this file
        pages = engine.get_pages_for_file("shared_file.py")
        self.assertEqual(len(pages), 5)
        for i in range(5):
            self.assertIn(f"page_{i}", pages)
        
        # Remove one page by clearing its sources
        page_to_delete = engine.get_page("page_2")
        page_to_delete.metadata.sources = []  # Clear sources to dissociate
        engine.save_page(page_to_delete)
        
        # Now only 4 pages should track the shared file
        pages_after = engine.get_pages_for_file("shared_file.py")
        self.assertEqual(len(pages_after), 4)
        self.assertNotIn("page_2", pages_after)

if __name__ == "__main__":
    unittest.main()

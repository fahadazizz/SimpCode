import unittest
import os
import tempfile
from simpcode.utils.hashes import calculate_file_hash, calculate_range_hash

class TestHashEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.test_dir.name, "test.txt")
        self.content = "line 1\nline 2\nline 3\nline 4\n"
        with open(self.test_file, "w") as f:
            f.write(self.content)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_file_hash(self):
        h = calculate_file_hash(self.test_file)
        self.assertEqual(len(h), 64) # SHA-256 length

    def test_range_hash(self):
        # Hash of lines 2 and 3
        h23 = calculate_range_hash(self.test_file, 2, 3)
        # Manually calculate for verification
        import hashlib
        expected = hashlib.sha256()
        expected.update("line 2\n".encode("utf-8"))
        expected.update("line 3\n".encode("utf-8"))
        self.assertEqual(h23, expected.hexdigest())

    def test_single_line_hash(self):
        h1 = calculate_range_hash(self.test_file, 1, 1)
        import hashlib
        expected = hashlib.sha256()
        expected.update("line 1\n".encode("utf-8"))
        self.assertEqual(h1, expected.hexdigest())

if __name__ == "__main__":
    unittest.main()

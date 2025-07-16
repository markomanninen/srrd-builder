import unittest
from pathlib import Path
import shutil
from work.code.mcp.storage.project_manager import ProjectManager

class TestProjectManager(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path("test_project")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_initialize_project(self):
        pm = ProjectManager(str(self.test_dir))
        result = pm.initialize_project("Test Project", "A test project", "testing")
        self.assertEqual(result["status"], "initialized")
        self.assertTrue((self.test_dir / ".srrd").exists())
        self.assertTrue((self.test_dir / ".git").exists())

if __name__ == '__main__':
    unittest.main()

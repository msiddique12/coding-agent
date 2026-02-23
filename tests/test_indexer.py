import unittest
import os
import shutil
import subprocess
import pickle
from unittest.mock import patch, MagicMock
import numpy as np
import git
from indexing.indexer import CodeIndexer

class TestIndexer(unittest.TestCase):
    def setUp(self):
        self.test_dir = "temp_indexer_test_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create a dummy git repo and commit .gitignore
        self.repo = git.Repo.init(self.test_dir)
        
        # Create dummy files
        with open(os.path.join(self.test_dir, "file1.py"), "w") as f:
            f.write("def hello():\n    print('hello')\n")
            
        with open(os.path.join(self.test_dir, "ignored_file.log"), "w") as f:
            f.write("this is a log")
            
        with open(os.path.join(self.test_dir, "dummy_binary.bin"), "wb") as f:
            f.write(b"this is some content with a \x00 null byte")
            
        os.makedirs(os.path.join(self.test_dir, "node_modules/lib"), exist_ok=True)
        with open(os.path.join(self.test_dir, "node_modules/lib/some_lib.js"), "w") as f:
            f.write("var x = 1;")

        # Create .gitignore
        with open(os.path.join(self.test_dir, ".gitignore"), "w") as f:
            f.write("*.log\nnode_modules/\n")
        
        self.repo.index.add([".gitignore"])
        self.repo.index.commit("Initial commit")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('indexing.indexer.git.Repo')
    @patch('indexing.indexer.SentenceTransformer')
    def test_indexing_process(self, MockSentenceTransformer, MockGitRepo):
        # Arrange
        # Make sure the indexer uses the repo from the test directory
        MockGitRepo.return_value = self.repo

        # Mock the sentence transformer to return a mock tensor
        mock_model = MagicMock()
        mock_embeddings_list = [np.array([0.1] * 384)] # One embedding for the one chunk
        
        # Create a mock tensor object that has .shape and can be used in .cpu().numpy()
        mock_tensor = MagicMock()
        mock_tensor.shape = (len(mock_embeddings_list), 384)
        mock_tensor.cpu.return_value.numpy.return_value = np.array(mock_embeddings_list)
        
        mock_model.encode.return_value = mock_tensor
        MockSentenceTransformer.return_value = mock_model

        index_path = os.path.join(self.test_dir, ".test_index.faiss")
        map_path = os.path.join(self.test_dir, ".test_index_map.pkl")
        
        indexer = CodeIndexer(index_path=index_path, map_path=map_path)
        
        # Act
        indexer.index_project(directory=self.test_dir)
        
        # Assert
        self.assertTrue(os.path.exists(index_path))
        self.assertTrue(os.path.exists(map_path))
        
        with open(map_path, 'rb') as f:
            data_map = pickle.load(f)
        
        # Only file1.py should be indexed
        self.assertEqual(len(data_map), 1) 
        self.assertEqual(data_map[0]["file_path"], os.path.join(self.test_dir, "file1.py"))
        self.assertIn("def hello", data_map[0]["content"])

if __name__ == '__main__':
    unittest.main()

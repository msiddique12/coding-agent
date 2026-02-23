import os
import faiss
from sentence_transformers import SentenceTransformer
import pickle
import git
from utils.filesystem import IGNORE_DIRS

INDEXABLE_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rs",
    ".sh",
    ".css",
    ".html",
    ".sql",
}

def is_binary(file_path, chunk_size=4096):
    """
    Check if a file is binary by reading a chunk and looking for null bytes.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            if b'\x00' in chunk:
                return True
        return False
    except Exception:
        # If we can't read the file, treat it as binary to be safe
        return True

class CodeIndexer:
    def __init__(self, model_name='all-MiniLM-L6-v2', index_path='.project_index.faiss', map_path='.project_index_map.pkl'):
        self.model = SentenceTransformer(model_name)
        self.index_path = index_path
        self.map_path = map_path

    def _get_git_repo(self):
        try:
            return git.Repo(search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            return None

    def _get_files_to_index(self, directory):
        repo = self._get_git_repo()
        repo_root = None
        if repo:
            try:
                repo_root = repo.working_tree_dir
            except Exception:
                repo_root = None

        files_to_index = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                file_path = os.path.join(root, file)
                if not self._is_indexable_text_file(file_path):
                    continue
                if self._is_git_ignored(file_path, repo, repo_root):
                    continue
                if not is_binary(file_path):
                    files_to_index.append(file_path)
        return files_to_index

    def _is_indexable_text_file(self, file_path):
        filename = os.path.basename(file_path)
        _, ext = os.path.splitext(filename)
        if filename.startswith("."):
            return False
        return ext.lower() in INDEXABLE_EXTENSIONS

    def _is_git_ignored(self, file_path, repo, repo_root):
        if not repo or not repo_root:
            return False

        try:
            relative_path = os.path.relpath(os.path.abspath(file_path), os.path.abspath(repo_root))
            if relative_path.startswith(".."):
                return False
            ignored = repo.ignored([relative_path])
            return bool(ignored)
        except Exception:
            return False

    def _chunk_file(self, file_path, chunk_size=15, overlap=5):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception:
            return []

        chunks = []
        for i in range(0, len(lines), chunk_size - overlap):
            chunk = lines[i:i + chunk_size]
            if chunk:
                chunks.append({
                    "file_path": file_path,
                    "start_line": i + 1,
                    "content": "".join(chunk)
                })
        return chunks

    def index_project(self, directory='.'):
        print("Starting project indexing...")
        files = self._get_files_to_index(directory)
        print(f"Found {len(files)} files to index.")

        all_chunks = []
        for file in files:
            all_chunks.extend(self._chunk_file(file))
        
        if not all_chunks:
            print("No content to index.")
            return

        print(f"Created {len(all_chunks)} chunks. Generating embeddings...")
        
        # Generate embeddings
        contents = [chunk['content'] for chunk in all_chunks]
        embeddings = self.model.encode(contents, convert_to_tensor=True, show_progress_bar=True)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(int(dimension))
        index.add(embeddings.cpu().numpy())
        
        # Save index and map
        faiss.write_index(index, self.index_path)
        with open(self.map_path, 'wb') as f:
            pickle.dump(all_chunks, f)
            
        print(f"Indexing complete. Index saved to {self.index_path} and map to {self.map_path}")

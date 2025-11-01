import os

IGNORE_DIRS = {'.git', 'venv', 'node_modules', '__pycache__', '.mypy_cache'}
IGNORE_FILES = {'agent.log'}

def list_code_files(root_dir="."):
    files_list = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [ d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            if fname in IGNORE_FILES:
                continue
            if fname.endswith(('.py', '.md', '.js', '.ts', '.ipynb', '.txt', '.json')):
                full_path = os.path.relpath(os.path.join(dirpath, fname), root_dir)
                files_list.append(full_path)
    return sorted(files_list)
        
def read_file(fp):
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"ERROR: {e}"
    
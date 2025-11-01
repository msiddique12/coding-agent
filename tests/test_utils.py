import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.filesystem import list_code_files, read_file

def test_list_files():
    files = list_code_files()
    print("Files found:", files)
    assert any(f.endswith(".py") for f in files)
    
def test_read_file():
    file = "README.md"
    content = read_file(file)
    
    print("Content of README.md:", content[:100])
    assert "error" not in content.lower()
    
if __name__ == "__main__":
    test_list_files()
    test_read_file()
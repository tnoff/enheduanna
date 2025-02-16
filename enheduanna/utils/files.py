from pathlib import Path
from typing import List

def list_markdown_files(file_dir: Path) -> List[Path]:
    '''
    List all markdown files in directory in order

    file_dir: Original file dir
    '''
    all_paths = []
    for path in file_dir.rglob('**/*.md'):
        all_paths.append(path)
    return sorted(all_paths, key=str)

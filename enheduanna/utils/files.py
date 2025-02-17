from pathlib import Path
from typing import List, Union

def list_markdown_files(file_dir: Path) -> List[Path]:
    '''
    List all markdown files in directory in order

    file_dir: Original file dir
    '''
    all_paths = []
    for path in file_dir.rglob('**/*.md'):
        all_paths.append(path)
    return sorted(all_paths, key=str)


def find_last_markdown_file(file_dir: Path) -> Union[None, Path]:
    '''
    In a dir, find the last file from the sorted list

    file_dir: File dir with files

    '''
    files = list_markdown_files(file_dir)
    if not files:
        return None
    return files[-1]

from pathlib import Path
from re import match
from typing import List, Union

# Assume daily notes only have numbers in name
MATCH_DAILY_NOTE = r'^([0-9-_]+).md$'

def list_markdown_files(file_dir: Path, only_include_daily_note: bool = True) -> List[Path]:
    '''
    List all markdown files in directory in order

    file_dir: Original file dir
    only_include_daily_note: Only include daily note files
    '''
    all_paths = []
    for path in file_dir.rglob('**/*.md'):
        if not path.is_file():
            continue
        if only_include_daily_note and not match(MATCH_DAILY_NOTE, path.name):
            continue
        all_paths.append(path)
    return sorted(all_paths, key=lambda x: x.name)


def find_last_markdown_file(file_dir: Path, only_include_daily_note: bool = True) -> Union[None, Path]:
    '''
    In a dir, find the last file from the sorted list

    file_dir: File dir with files
    only_include_daily_note: Only include daily note files
    '''
    files = list_markdown_files(file_dir, only_include_daily_note=only_include_daily_note)
    if not files:
        return None
    return files[-1]

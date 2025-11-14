from pathlib import Path
from re import match
from string import digits, ascii_lowercase, ascii_uppercase
from typing import List, Union

# Assume entries only have numbers in name
MATCH_ENTRY = r'^([0-9-_]+).md$'

VALID_FILENAME_CHARS = ascii_uppercase + ascii_lowercase + digits + ' -._'

def list_markdown_files(file_dir: Path, only_include_entry: bool = True) -> List[Path]:
    '''
    List all markdown files in directory in order

    file_dir: Original file dir
    only_include_entry: Only include entry files (date-based names)
    '''
    all_paths = []
    for path in file_dir.rglob('**/*.md'):
        if not path.is_file():
            continue
        if only_include_entry and not match(MATCH_ENTRY, path.name):
            continue
        all_paths.append(path)
    return sorted(all_paths, key=lambda x: x.name)


def find_last_markdown_file(file_dir: Path, only_include_entry: bool = True) -> Union[None, Path]:
    '''
    In a dir, find the last file from the sorted list

    file_dir: File dir with files
    only_include_entry: Only include entry files (date-based names)
    '''
    files = list_markdown_files(file_dir, only_include_entry=only_include_entry)
    if not files:
        return None
    return files[-1]

def normalize_file_name(file_name: str) -> str:
    '''
    Normalize filename to remove non string and non digit characters
    '''
    new_string = ''
    for char in file_name:
        if char in VALID_FILENAME_CHARS:
            new_string = f'{new_string}{char}'
            continue
        new_string = f'{new_string}_'
    return new_string

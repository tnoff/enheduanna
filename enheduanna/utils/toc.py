from pathlib import Path
from typing import List, Union
import os

from enheduanna.types.config.toc import TocConfig
from enheduanna.types.markdown.markdown_file import MarkdownFile
from enheduanna.types.markdown.markdown_section import MarkdownSection


def _relative_link(target: Path, base_dir: Path) -> str:
    '''
    Build a "./"-prefixed relative link target from base_dir to target

    target : File the link points at
    base_dir : Directory the link is written from
    '''
    return f'./{os.path.relpath(target, base_dir)}'


def build_summary_toc_section(file_dir: Path, markdown_files: List[MarkdownFile],
                              media_extensions: List[str], toc_config: TocConfig) -> Union[MarkdownSection, None]:
    '''
    Build a table of contents section linking to entry files and collated media

    file_dir : Collation folder the summary is written into
    markdown_files : Entry markdown files being collated
    media_extensions : File extensions treated as media
    toc_config : Table of contents configuration

    Returns a MarkdownSection, or None when there is nothing to link
    '''
    toc_section = MarkdownSection(toc_config.summary_title, '', level=2)
    if toc_config.include_entries:
        entry_lines = []
        for markdown_file in markdown_files:
            link = _relative_link(markdown_file.file_path, file_dir)
            entry_lines.append(f'- [{markdown_file.root_section.title}]({link})')
        if entry_lines:
            toc_section.add_section(MarkdownSection('Entries', '\n'.join(entry_lines), level=3))
    if toc_config.include_media:
        extensions = [ext.lower() for ext in media_extensions]
        media_paths = sorted(path for path in file_dir.rglob('*')
                             if path.is_file() and path.suffix.lower() in extensions)
        media_lines = []
        for path in media_paths:
            link = _relative_link(path, file_dir)
            media_lines.append(f'- [{path.name}]({link})')
        if media_lines:
            toc_section.add_section(MarkdownSection('Media', '\n'.join(media_lines), level=3))
    if not toc_section.sections:
        return None
    return toc_section


def update_root_index(entries_folder: Path, collate_name: str, toc_config: TocConfig) -> Union[Path, None]:
    '''
    Create or refresh the root index file that links to each collation summary

    entries_folder : Folder holding all collation subfolders
    collate_name : Name of the summary file within each collation folder
    toc_config : Table of contents configuration

    Returns the path to the written index file, or None when there is nothing to index
    '''
    folders = sorted((child for child in entries_folder.iterdir()
                      if child.is_dir() and (child / collate_name).exists()), reverse=True)
    if not folders:
        return None
    lines = []
    for folder in folders:
        pretty = folder.name.replace('_', ' -> ')
        lines.append(f'- [{pretty}](./{folder.name}/{collate_name})')
    index_section = MarkdownSection(toc_config.root_index_title, '\n'.join(lines), level=1)
    index_path = entries_folder / toc_config.root_index_name
    index_path.write_text(index_section.write())
    return index_path

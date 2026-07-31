from copy import deepcopy
from json import dumps
from pathlib import Path
from typing import List, Tuple

from enheduanna.types.markdown.markdown_file import MarkdownFile
from enheduanna.types.markdown.markdown_section import MarkdownSection
from enheduanna.types.markdown.collate_section import CollateSection
from enheduanna.types.markdown.document_section import DocumentSection
from enheduanna.utils.files import normalize_file_name
from enheduanna.utils.links import rewrite_section_links

def section_generate_from_json(data_input: List[dict]) -> List[MarkdownSection]:
    '''
    Generate MarkdownSection input from list of dicts

    data_input : List of dicts with Markdown Section input
    '''
    return_data = []
    for section in data_input:
        return_data.append(MarkdownSection.from_json(dumps(section)))
    return return_data

def collate_section_generate_from_json(data_input: List[dict]) -> List[CollateSection]:
    '''
    Generate CollateSections from list of strings

    data_input : List of strings for titles
    '''
    return_data = []
    for section in data_input:
        return_data.append(CollateSection.from_json(dumps(section)))
    return return_data

def _gather_all_section_data(markdown_file: MarkdownFile, parent_section: MarkdownSection,
                             collate_sections: List[str], ignore_sections: List[str],
                             collate_mapping: dict, document_list: list,
                             document_folder: Path) -> bool:
    '''
    Recursively gather all section data in collate section names

    markdown_file : Original markdown file
    parent_section : Section before this call
    markdown_sections: Sections within parent
    collate_sections: Collate sections to run
    ignore_sections: Ignore these sections for doc collation
    document_folder: Destination folder for extracted document sections

    collate_mapping/document_list: Kept here for loop to return in main function
    '''
    doc_sections = []
    for section in parent_section.sections:
        if section.title in ignore_sections:
            continue
        match_found = False
        for collate_section in collate_sections:
            if section.title == collate_section.title and section.level == collate_section.level:
                if section.title not in collate_mapping:
                    collate_mapping[section.title] = {
                        'section': deepcopy(section),
                        'collate': collate_section,
                    }
                else:
                    collate_mapping[section.title]['section'].merge(section)
                match_found = True
                continue

        if not match_found:
            if section.level > 1:
                doc_sections.append(section.title)
                continue
            _gather_all_section_data(markdown_file, section, collate_sections, ignore_sections, collate_mapping, document_list, document_folder)
    # Remove these at the end since it cant muck with the order of sections
    for title in doc_sections:
        document_section = parent_section.remove_section(title)
        markdown_file.write()
        new_root = document_section.generate_root(prefix=f'{markdown_file.root_section.title} ')
        # Relative links resolve against the source file's dir; fix them for the new location.
        # Pass the (already-trimmed) source root so anchors to headings that stayed behind
        # become cross-file links.
        rewrite_section_links(new_root, markdown_file.file_path, document_folder, markdown_file.root_section)
        # Keep the un-prefixed title alongside the dated root so the writer can match an
        # existing aggregator file (e.g. "Greg Weekly.md") named after the base section.
        document_list.append(DocumentSection(base_title=title, root=new_root))

    return True

def generate_markdown_collation(markdown_files: List[MarkdownFile], collate_sections: List[CollateSection],
                             ignore_sections: List[str], document_folder: Path) -> Tuple[List[MarkdownSection], List[DocumentSection]]:
    '''
    Combine markdown sections by the collate titles

    markdown_sections: Sections of markdown
    collate_sections: List of collate sections
    ignore_sections: Ignore sections when making new documents
    document_folder: Destination folder for extracted document sections

    returns tupe of [List of combined sections] [List of DocumentSections]
    '''
    section_mapping = {}
    document_list = []
    for markdown_file in markdown_files:
        _gather_all_section_data(markdown_file, markdown_file.root_section, collate_sections, ignore_sections, section_mapping, document_list, document_folder)
    new_sections = []
    for _key, values in section_mapping.items():
        section = values['section']
        section.group_contents(values['collate'])
        new_sections.append(section)
    return new_sections, document_list

def write_document_section(document: DocumentSection, document_folder: Path) -> Tuple[Path, bool]:
    '''
    Write an extracted document section to the document folder

    If an aggregator file named "<base_title>.md" already exists in the folder, the dated
    section is appended to the bottom of it as a new sub-section. Otherwise a standalone
    "<date> <base_title>.md" file is written (the original behaviour).

    document : DocumentSection to write
    document_folder : Destination folder for documents

    returns tuple of (written path, whether it was appended to an existing aggregator)
    '''
    aggregate_path = document_folder / f'{normalize_file_name(document.base_title)}.md'
    if aggregate_path.exists():
        # An empty aggregator file (e.g. freshly `touch`ed) has no title to parse, so seed a
        # root titled after the base section instead of parsing it into a section-less root.
        if aggregate_path.read_text().strip():
            markdown_file = MarkdownFile.from_file(aggregate_path)
        else:
            markdown_file = MarkdownFile(aggregate_path, MarkdownSection(document.base_title, ''))
        section = document.root
        section.level = markdown_file.root_section.level + 1
        section.set_section_levels(section.level + 1)
        # Append directly rather than via add_section: re-running collate can legitimately add
        # a second section with the same "<date> <base_title>" title, which add_section rejects.
        markdown_file.root_section.sections.append(section)
        markdown_file.write()
        return aggregate_path, True
    standalone_path = document_folder / f'{normalize_file_name(document.root.title)}.md'
    MarkdownFile(standalone_path, document.root).write()
    return standalone_path, False

def __remove_empty(markdown_file: MarkdownFile, parent_section: MarkdownSection) -> bool:
    remove_sections = []
    for section in parent_section.sections:
        __remove_empty(markdown_file, section)
        if section.is_empty():
            remove_sections.append(section.title)

    for remove in remove_sections:
        parent_section.remove_section(remove)
    return True

def generate_markdown_merge(markdown_files: List[MarkdownFile], title: str, output_dir: Path) -> MarkdownSection:
    '''
    Merge all markdown files into a single section, with each file becoming a section
    and all subsections increased by 1 level

    markdown_files: List of markdown files to merge
    title: Title for the merged document
    output_dir: Destination folder for the merged file

    returns merged MarkdownSection
    '''
    merged_root = MarkdownSection(title, '')

    for markdown_file in markdown_files:
        # Create a copy of the root section from the file
        file_section = deepcopy(markdown_file.root_section)
        # Relative links resolve against the source file's dir; fix them for the new location.
        # The whole file moves, so every same-file anchor moves with it (no stayed-behind root).
        rewrite_section_links(file_section, markdown_file.file_path, output_dir)
        # Increase level to 2 (from 1) and all subsections accordingly
        file_section.level = 2
        file_section.set_section_levels(3)
        # Add this file as a section in the merged document
        merged_root.add_section(file_section)

    return merged_root

def remove_empty_sections(markdown_files: List[MarkdownFile]) -> bool:
    '''
    Remove empty exections from markdown files

    markdown_files : List of markdown files
    '''
    for mf in markdown_files:
        __remove_empty(mf, mf.root_section)
        mf.write()

from copy import deepcopy
from typing import List, Tuple

from enheduanna.types.markdown.markdown_file import MarkdownFile
from enheduanna.types.markdown.markdown_section import MarkdownSection
from enheduanna.types.markdown.markdown_merge_setting import MarkdownMergeSetting

def _gather_all_section_data(markdown_file: MarkdownFile, parent_section: MarkdownSection,
                             markdown_merge_settings: List[str], ignore_sections: List[str],
                             rollup_mapping: dict, document_list: list) -> bool:
    '''
    Recursively gather all section data in rollup section names

    markdown_file : Original markdown file
    parent_section : Section before this call
    markdown_sections: Sections within parent
    markdown_merge_settings: Rollup sections to run
    ignore_sections: Ignore these sections for doc rollup

    rollup_mapping/document_list: Kept here for loop to return in main function
    '''
    doc_sections = []
    for section in parent_section.sections:
        if section.title in ignore_sections:
            continue
        match_found = False
        for markdown_merge_setting in markdown_merge_settings:
            if section.title == markdown_merge_setting.title and section.level == markdown_merge_setting.level:
                if section.title not in rollup_mapping:
                    rollup_mapping[section.title] = {
                        'section': deepcopy(section),
                        'rollup': markdown_merge_setting,
                    }
                else:
                    rollup_mapping[section.title]['section'].merge(section)
                match_found = True
                continue

        if not match_found:
            if section.level > 1:
                doc_sections.append(section.title)
                continue
            _gather_all_section_data(markdown_file, section, markdown_merge_settings, ignore_sections, rollup_mapping, document_list)
    # Remove these at the end since it cant muck with the order of sections
    for title in doc_sections:
        document_section = parent_section.remove_section(title)
        markdown_file.write()
        document_list.append(document_section.generate_root(prefix=f'{markdown_file.root_section.title} '))

    return True

def generate_markdown_rollup(markdown_files: List[MarkdownFile], markdown_merge_settings: List[MarkdownMergeSetting],
                             ignore_sections: List[str]) -> Tuple[List[MarkdownSection], List[MarkdownSection]]:
    '''
    Combine markdown sections by the rollup titles

    markdown_sections: Sections of markdown
    markdown_merge_settings: List of rollup sections
    ignore_sections: Ignore sections when making new documents

    returns tupe of [List of combined sections] [List of document sections]
    '''
    section_mapping = {}
    document_list = []
    for markdown_file in markdown_files:
        _gather_all_section_data(markdown_file, markdown_file.root_section, markdown_merge_settings, ignore_sections, section_mapping, document_list)
    new_sections = []
    for _key, values in section_mapping.items():
        section = values['section']
        section.group_contents(values['rollup'])
        new_sections.append(section)
    return new_sections, document_list

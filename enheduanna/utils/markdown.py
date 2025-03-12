from copy import deepcopy
from typing import List, Tuple

from enheduanna.types.markdown.markdown_file import MarkdownFile
from enheduanna.types.markdown.markdown_section import MarkdownSection
from enheduanna.types.markdown.rollup_section import RollupSection

def _gather_all_section_data(markdown_file: MarkdownFile, parent_section: MarkdownSection,
                             rollup_sections: List[str], ignore_sections: List[str],
                             rollup_mapping: dict, document_list: list) -> bool:
    '''
    Recursively gather all section data in rollup section names

    markdown_file : Original markdown file
    parent_section : Section before this call
    markdown_sections: Sections within parent
    rollup_sections: Rollup sections to run
    ignore_sections: Ignore these sections for doc rollup

    rollup_mapping/document_list: Kept here for loop to return in main function
    '''
    doc_sections = []
    for section in parent_section.sections:
        if section.title in ignore_sections:
            continue
        match_found = False
        for rollup_section in rollup_sections:
            if section.title == rollup_section.title and section.level == rollup_section.level:
                if section.title not in rollup_mapping:
                    rollup_mapping[section.title] = {
                        'section': deepcopy(section),
                        'rollup': rollup_section,
                    }
                else:
                    rollup_mapping[section.title]['section'].merge(section)
                match_found = True
                continue

        if not match_found:
            if section.level > 1:
                doc_sections.append(section.title)
                continue
            _gather_all_section_data(markdown_file, section, rollup_sections, ignore_sections, rollup_mapping, document_list)
    # Remove these at the end since it cant muck with the order of sections
    for title in doc_sections:
        document_section = parent_section.remove_section(title)
        markdown_file.write()
        document_list.append(document_section.generate_root(prefix=f'{markdown_file.root_section.title} '))

    return True

def generate_markdown_rollup(markdown_files: List[MarkdownFile], rollup_sections: List[RollupSection],
                             ignore_sections: List[str]) -> Tuple[List[MarkdownSection], List[MarkdownSection]]:
    '''
    Combine markdown sections by the rollup titles

    markdown_sections: Sections of markdown
    rollup_sections: List of rollup sections
    ignore_sections: Ignore sections when making new documents

    returns tupe of [List of combined sections] [List of document sections]
    '''
    section_mapping = {}
    document_list = []
    for markdown_file in markdown_files:
        _gather_all_section_data(markdown_file, markdown_file.root_section, rollup_sections, ignore_sections, section_mapping, document_list)
    new_sections = []
    for _key, values in section_mapping.items():
        section = values['section']
        section.group_contents(values['rollup'])
        new_sections.append(section)
    return new_sections, document_list

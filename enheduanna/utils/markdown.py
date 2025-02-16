from json import dumps
from re import search
from typing import List

from enheduanna.types.markdown_section import MarkdownSection
from enheduanna.types.rollup_section import RollupSection

class MarkdownParserException(Exception):
    '''
    Markdown parser exceptions
    '''

def section_generate_from_json(data_input: List[dict]) -> List[MarkdownSection]:
    '''
    Generate MarkdownSection input from list of dicts

    data_input : List of dicts with Markdown Section input
    '''
    return_data = []
    for section in data_input:
        return_data.append(MarkdownSection.from_json(dumps(section)))
    return return_data

def rollup_section_generate_from_json(data_input: List[dict]) -> List[RollupSection]:
    '''
    Generate RollupSections from list of strings

    data_input : List of strings for titles
    '''
    return_data = []
    for section in data_input:
        return_data.append(RollupSection.from_json(dumps(section)))
    return return_data

def _gather_all_section_data(markdown_sections: List[MarkdownSection], rollup_sections: List[str], rollup_mapping: dict) -> bool:
    '''
    Recursively gather all section data in rollup section names
    '''
    for section in markdown_sections:
        for rollup_section in rollup_sections:
            if section.title == rollup_section.title:
                rollup_mapping.setdefault(section.title, {
                    'contents': '',
                    'regex': rollup_section.regex,
                    'groupBy': rollup_section.groupBy,
                })
                rollup_mapping[section.title]['contents'] += f'{section.contents}\n'
        _gather_all_section_data(section.sections, rollup_sections, rollup_mapping)
    return True

def combine_markdown_sections(markdown_sections: List[MarkdownSection], rollup_sections: List[RollupSection]) -> List[MarkdownSection]:
    '''
    Combine markdown sections by the rollup titles

    markdown_sections: Sections of markdown
    rollup_sections: List of rollup sections
    '''

    section_mapping = {}
    _gather_all_section_data(markdown_sections, rollup_sections, section_mapping)
    return_data = []
    for section, section_data in section_mapping.items():
        if not section_data['regex']:
            return_data.append(MarkdownSection(section, section_data['contents']))
            continue
        matches_mapping = {}
        not_matching = ''
        for content in section_data['contents'].split('\n'):
            matcher = search(section_data['regex'], content)
            if matcher:
                groupBy = matcher.group(section_data['groupBy'])
                matches_mapping.setdefault(groupBy, '')
                matches_mapping[groupBy] += f'{content}\n'
                continue
            not_matching += f'{content}\n'
        generated_content = ''
        for _groupBy, contents in matches_mapping.items():
            generated_content += f'{contents}\n'
        generated_content += f'{not_matching}\n'
        return_data.append(MarkdownSection(section, generated_content))
    # Final touchups to content
    for section in return_data:
        section.contents = f'{section.contents.rstrip()}'
    return return_data

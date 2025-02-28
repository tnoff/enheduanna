from json import dumps
from typing import List

from pathlib import Path
from pydantic import Field
from pydantic.dataclasses import dataclass

from enheduanna.types.markdown_section import MarkdownSection
from enheduanna.types.rollup_section import RollupSection

NOTE_DIR_DEFAULT = Path.home() / 'Notes'
DOCUMENT_DIR_DEFAULT = Path.home() / 'Documents'
DATE_FORMAT_DEFAULT = '%Y-%m-%d'

def daily_file_section_generate_from_json(data_input: List[dict]) -> List[MarkdownSection]:
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

DAILY_FILE_SECTIONS_DEFAULT = [
    MarkdownSection('Work Done', '- ', level=2),
    MarkdownSection('Meetings', '| Time | Meeting Name |\n| ---- | ------------ |\n| | |', level=2),
    MarkdownSection('Follow Ups', '- ', level=2, carryover=True),
    MarkdownSection('Scratch', '', level=2),
]

ROLLUP_SECTIONS_DEFAULT = [
    RollupSection('Work Done', regex='\\((?P<ticket>[A-Za-z]+-[0-9]+)\\)', groupBy='ticket', level=2),
]

@dataclass
class CliFileConfig:
    '''
    Cli config for file options
    '''
    note_folder: Path = NOTE_DIR_DEFAULT
    document_folder: Path = DOCUMENT_DIR_DEFAULT
    date_format: str = DATE_FORMAT_DEFAULT

    daily_file_sections: list[dict] = Field(default_factory=list)
    rollup_sections: list[dict] = Field(default_factory=list)

    def __post_init__(self):
        self.daily_file_sections = daily_file_section_generate_from_json(self.daily_file_sections) or DAILY_FILE_SECTIONS_DEFAULT
        self.rollup_sections = rollup_section_generate_from_json(self.rollup_sections) or ROLLUP_SECTIONS_DEFAULT
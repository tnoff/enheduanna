from pathlib import Path
from typing import Self, List

from pydantic import Field
from pydantic import model_validator
from pydantic.dataclasses import dataclass

from enheduanna.defaults import NOTE_DIR_DEFAULT, DOCUMENT_DIR_DEFAULT, DATE_OUTPUT_FORMAT_DEFAULT
from enheduanna.types.markdown_section import MarkdownSection
from enheduanna.types.rollup_section import RollupSection

DAILY_SECTIONS_DEFAULT = [
    MarkdownSection('Work Done', '- ', level=2),
    MarkdownSection('Meetings', '| Time | Meeting Name |\n| ---- | ------------ |\n| | |', level=2),
    MarkdownSection('Follow Ups', '- ', level=2, carryover=True),
    MarkdownSection('Scratch', '- ', level=2)
]

ROLLUP_SECTIONS_DEFAULT = [
    RollupSection('Work Done', regex='\\((?P<ticket>[A-Za-z]+-[0-9]+)\\)', groupBy='ticket', level=2)
]

@dataclass
class FileConfig:
    '''
    Config file options
    '''
    note_directory: Path = NOTE_DIR_DEFAULT
    document_directory: Path = DOCUMENT_DIR_DEFAULT
    date_output_format: str = DATE_OUTPUT_FORMAT_DEFAULT

    daily_sections: List[MarkdownSection] = Field(default_factory=list)
    rollup_sections: List[RollupSection] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_daily_sections(self) -> Self:
        '''
        Validate daily sections bits
        '''
        if not self.daily_sections:
            self.daily_sections = DAILY_SECTIONS_DEFAULT
        return self

    @model_validator(mode='after')
    def validate_rollup_sections(self) -> Self:
        '''
        Validate rollups bits
        '''
        if not self.rollup_sections:
            self.rollup_sections = ROLLUP_SECTIONS_DEFAULT
        return self

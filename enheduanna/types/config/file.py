from pathlib import Path
from typing import Self, List

from pydantic import Field
from pydantic import model_validator
from pydantic.dataclasses import dataclass

from enheduanna.defaults import ENTRIES_DIR_DEFAULT, DOCUMENT_DIR_DEFAULT, DATE_OUTPUT_FORMAT_DEFAULT
from enheduanna.types.markdown.markdown_section import MarkdownSection
from enheduanna.types.markdown.collate_section import CollateSection

ENTRY_SECTIONS_DEFAULT = [
    MarkdownSection('Work Done', '- ', level=2),
    MarkdownSection('Meetings', '| Time | Meeting Name |\n| ---- | ------------ |\n| | |', level=2),
    MarkdownSection('Follow Ups', '- ', level=2, rollover=True),
    MarkdownSection('Scratch', '- ', level=2)
]

COLLATE_SECTIONS_DEFAULT = [
    CollateSection('Work Done', regex='\\((?P<ticket>[A-Za-z]+-[0-9]+)\\)', groupBy='ticket', level=2)
]

@dataclass
class FileConfig:
    '''
    Config file options
    '''
    entries_directory: Path = ENTRIES_DIR_DEFAULT
    document_directory: Path = DOCUMENT_DIR_DEFAULT
    date_output_format: str = DATE_OUTPUT_FORMAT_DEFAULT

    entry_sections: List[MarkdownSection] = Field(default_factory=list)
    collate_sections: List[CollateSection] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_entry_sections(self) -> Self:
        '''
        Validate entry sections bits
        '''
        if not self.entry_sections:
            self.entry_sections = ENTRY_SECTIONS_DEFAULT
        return self

    @model_validator(mode='after')
    def validate_collate_sections(self) -> Self:
        '''
        Validate collate bits
        '''
        if not self.collate_sections:
            self.collate_sections = COLLATE_SECTIONS_DEFAULT
        return self

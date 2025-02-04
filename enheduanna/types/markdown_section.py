from typing import Self

from pydantic import Field
from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass

@dataclass
class MarkdownSection:
    '''
    Markdown Sections for writing
    '''
    title: str
    contents: str
    level: int = Field(default=1)
    sections: list[Self] = Field(default_factory=list)

    def add_section(self, section: Self):
        '''
        Add a new section

        section : MarkdownSection
        '''
        TypeAdapter(MarkdownSection).validate_python(section)
        self.sections.append(section)

    def __str__(self):
        return self.title

MarkdownSection.from_json = TypeAdapter(MarkdownSection).validate_json

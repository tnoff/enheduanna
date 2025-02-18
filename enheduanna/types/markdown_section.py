from typing import Self, Union

from pydantic import Field
from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass

class MarkdownException(Exception):
    '''
    Generic class for exception errors
    '''

@dataclass
class MarkdownSection:
    '''
    Markdown Sections for writing
    '''
    title: str
    contents: str
    level: int = Field(default=1)
    sections: list[Self] = Field(default_factory=list)
    carryover: bool = False

    def add_section(self, section: Self) -> bool:
        '''
        Add a new section

        section : MarkdownSection
        '''
        TypeAdapter(MarkdownSection).validate_python(section)
        # Check if section name already exists
        for existing_section in self.sections:
            if section.title == existing_section.title:
                raise MarkdownException(f'Cannot add section, a section with title "{existing_section.title}" already exists')
        self.sections.append(section)
        return True

    def remove_section(self, title: str) -> Union[Self, None]:
        '''
        Remove section with title

        title: Title of section to remove
        '''
        index = None
        for (count, section) in enumerate(self.sections):
            if section.title == title:
                index = count
                break
        if index is None:
            return None
        return self.sections.pop(index)

    def write(self) -> str:
        '''
        Get markdown output as string
        '''
        prefix = '#' * self.level
        out = f'{prefix} {self.title}\n'
        if self.contents:
            out = f'{out}\n{self.contents}\n'
        for section in self.sections:
            out = f'{out}\n{section.write()}'
        return out

    def __str__(self):
        return self.title

MarkdownSection.from_json = TypeAdapter(MarkdownSection).validate_json

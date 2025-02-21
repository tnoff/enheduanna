from copy import deepcopy
from re import search
from typing import Self, Union

from pydantic import Field
from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass

from enheduanna.types.rollup_section import RollupSection

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

    def set_section_levels(self, level: int) -> bool:
        '''
        Set section levels of all subsections
        '''
        for section in self.sections:
            section.level = level
            section.set_section_levels(level + 1)

    def generate_root(self, prefix: str=None) -> Self:
        '''
        Generate section as root, set level to 1 and all sub-sections accordingly
        
        prefix : Add prefix to new title file
        '''
        new_obj = deepcopy(self)
        if prefix:
            new_obj.title = f'{prefix}{self.title}'
        new_obj.level = 1
        new_obj.set_section_levels(2)
        return new_obj

    def merge(self, new_section: Self) -> bool:
        '''
        Merge this section with another one

        new_section : New section to merge with
        '''
        if new_section.title == self.title and new_section.level == self.level:
            self.contents = f'{self.contents}\n{new_section.contents}\n'
        # First see if any of our sub-sections are in the new one, remove and add
        for section in self.sections:
            result = new_section.remove_section(section.title)
            if not result:
                continue
            section.merge(result)
        # Then add remaining sections to this one
        for section in new_section.sections:
            self.add_section(section)
        return True

    def group_contents(self, rollup_section: RollupSection, force_grouping: bool = False) -> bool:
        '''
        Group contents by a rollup section regex

        rollup_section : RollupSection to group by
        force_grouping : Force grouping on subsections
        '''
        if not force_grouping and not rollup_section.regex and self.title != rollup_section.title:
            return False
        matching = {}
        non_matching = []
        for item in self.contents.split('\n'):
            if not item:
                continue
            matcher = search(rollup_section.regex, item)
            if matcher:
                key = matcher.group(rollup_section.groupBy)
                matching.setdefault(key, [])
                matching[key].append(item)
                continue
            non_matching.append(item)
        new_contents = ''
        for _key, value in matching.items():
            for item in value:
                new_contents = f'{new_contents}{item}\n'
            new_contents = f'{new_contents}\n'
        for item in non_matching:
            new_contents = f'{new_contents}{item}\n'
        new_contents = new_contents.rstrip()
        self.contents = new_contents
        for section in self.sections:
            section.group_contents(rollup_section, force_grouping=True)
        return True

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

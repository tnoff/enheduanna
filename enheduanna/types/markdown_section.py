from typing import Self, List, Union

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

def find_header(line_input: str) -> int:
    '''
    Find header if it exists in line and returns level

    line_input : Line that was inputed
    '''
    return len(line_input) - len(line_input.replace('#', ''))

def generate_markdown_sections(markdown_text: str, current_tab: int = 1) -> List[MarkdownSection]:
    '''
    Generate markdown section data from string

    markdown_data : Markdown data input
    current_tab : Keep track of tab number for recursive runs
    '''
    per_line = markdown_text.split('\n')
    title = None
    contents = ''
    subsection_contents = ''
    sections = []
    hit_sub_section = False
    for line in per_line:
        # Skip blank lines
        if not line:
            continue
        header_result = find_header(line)
        # If title not set, set that
        if header_result == current_tab and not title:
            title = line.lstrip().lstrip('#').lstrip()
            continue
        # If we hit the next level in
        if header_result == current_tab + 1:
            # Mark were in the next level, if we have subsections, assume we generate now
            hit_sub_section = True
            if subsection_contents:
                sections.append(generate_markdown_sections(subsection_contents, current_tab=current_tab+1))
                subsection_contents = f'{line}\n'
                hit_sub_section = True
                continue
        # Add to subsection or current contents
        if hit_sub_section:
            subsection_contents = f'{subsection_contents}{line}\n'
        else:
            contents = f'{contents}{line}\n'

    # We probably ended in a subsection
    if subsection_contents:
        sections.append(generate_markdown_sections(subsection_contents, current_tab=current_tab+1))
    ms = MarkdownSection(title, contents.rstrip('\n'), level=current_tab)
    for section in sections:
        ms.add_section(section)
    return ms

MarkdownSection.from_json = TypeAdapter(MarkdownSection).validate_json
MarkdownSection.from_text = generate_markdown_sections

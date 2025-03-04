from pathlib import Path
from typing import List

from pydantic.dataclasses import dataclass

from enheduanna.types.markdown.markdown_section import MarkdownSection

@dataclass
class MarkdownFile:
    '''
    Markdown File with path and sections
    '''
    file_path: Path
    root_section: MarkdownSection

    def write(self) -> bool:
        '''
        Write latest root section to file
        '''
        self.file_path.write_text(self.root_section.write())

    def __str__(self) -> str:
        '''
        Str func
        '''
        return f'{self.file_path}'


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

def from_file(file_path: Path) -> MarkdownFile:
    '''
    Generate Markdown file from file path

    file_path : New file path
    '''
    root_section = generate_markdown_sections(file_path.read_text())
    return MarkdownFile(file_path, root_section)

MarkdownFile.from_file = from_file

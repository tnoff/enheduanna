from pydantic.dataclasses import dataclass

from enheduanna.types.markdown.markdown_section import MarkdownSection

@dataclass
class DocumentSection:
    '''
    A document section extracted from an entry file during collation

    base_title : Section title without the date prefix, used to match an
                 existing aggregator file in the document folder
    root : Root MarkdownSection titled "<date> <base_title>"
    '''
    base_title: str
    root: MarkdownSection

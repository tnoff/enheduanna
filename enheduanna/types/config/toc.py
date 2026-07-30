from pydantic.dataclasses import dataclass

@dataclass
class TocConfig:
    '''
    Table of contents config options
    '''
    enabled: bool = True
    summary_title: str = 'Contents'
    include_entries: bool = True
    include_media: bool = True
    root_index_enabled: bool = True
    root_index_name: str = 'index.md'
    root_index_title: str = 'Notes Index'

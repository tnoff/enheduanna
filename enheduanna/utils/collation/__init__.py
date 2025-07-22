from datetime import date
from pathlib import Path

from enheduanna.types.config import Config
from enheduanna.types.config.collation import CollationType
from enheduanna.types.markdown.markdown_file import MarkdownFile
from enheduanna.types.markdown.markdown_section import MarkdownSection
from enheduanna.utils.collation.days import get_end_of_month, get_end_of_week, get_start_of_month, get_start_of_week

def create_parent_folder(config: Config, today: date) -> Path:
    '''
    Create weekly folder
    config: Complete config
    '''

    config.file.note_directory.mkdir(exist_ok=True)
    match config.collation.type:
        case CollationType.MONTHLY:
            start = get_start_of_month(today)
            end = get_end_of_month(today)
            parent_folder = config.file.note_directory / f'{start.strftime(config.file.date_output_format)}_{end.strftime(config.file.date_output_format)}'
        case _:
            start = get_start_of_week(today)
            end = get_end_of_week(today)
            parent_folder = config.file.note_directory / f'{start.strftime(config.file.date_output_format)}_{end.strftime(config.file.date_output_format)}'
    parent_folder.mkdir(exist_ok=True)
    return parent_folder

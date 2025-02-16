from datetime import date, timedelta
from pathlib import Path
from typing import List

import click
from pyaml_env import parse_config
from pydantic import ValidationError

from enheduanna.types.markdown_section import MarkdownSection

from enheduanna.utils.days import get_end_of_week, get_start_of_week
from enheduanna.utils.files import list_markdown_files
from enheduanna.utils.markdown import section_generate_from_json
from enheduanna.utils.markdown import rollup_section_generate_from_json
from enheduanna.utils.markdown import generate_markdown_sections
from enheduanna.utils.markdown import combine_markdown_sections
from enheduanna.utils.markdown import markdown_section_output

class ConfigException(Exception):
    '''
    Generic Exception for config errors
    '''

CONFIG_DEFAULT = Path.home() / '.enheduanna.yml'
FOLDER_DEFAULT = Path.home() / 'Notes'
DATE_FORMAT_DEFAULT = '%Y-%m-%d'

SECTIONS_DEFAULT = [
    {
        'title': 'Work Done',
        'contents': '\n- ',
        'level': 2,
    },
    {
        'title': 'Meetings',
        'contents': '\n| Time | Meeting Name |\n| ---- | ------------ |\n| | |',
        'level': 2,
    },
    {
        'title': 'Follow Ups',
        'contents': '\n- ',
        'level': 2,
    },
    {
        'title': 'Scratch',
        'contents': '',
        'level': 2,
    }
]

ROLLUP_SECTIONS_DEFAULT = [
    {
        'title': 'Work Done',
        'regex': '\\((?P<ticket>[A-Za-z]+-[0-9]+)\\)',
        'groupBy': 'ticket',
    },
    {
        'title': 'Follow Ups',
    }
]

def get_config_options(config: dict, note_folder: str, date_format: str) -> dict:
    '''
    Get config options from config file and cli
    config : Config dictionary
    note_folder : Note folder cli override
    date_format : Date format cli override
    '''
    if note_folder is not None:
        config['note_folder'] = Path(note_folder)
    else:
        config['note_folder'] = Path(config.get('note_folder', FOLDER_DEFAULT))

    if date_format is not None:
        config['date_format'] = date_format
    else:
        config['date_format'] = config.get('date_format', DATE_FORMAT_DEFAULT)
    try:
        config['sections'] = section_generate_from_json(config.get('sections', SECTIONS_DEFAULT))
    except ValidationError as e:
        raise ConfigException('Invalid section config given') from e
    try:
        config['rollup_sections'] = rollup_section_generate_from_json(config.get('rollup_sections', ROLLUP_SECTIONS_DEFAULT))
    except ValidationError as e:
        raise ConfigException('Invalid rollup sections given') from e
    return config

def create_weekly_folder(note_folder: Path, start: date, end: date, date_format: str) -> Path:
    '''
    Create weekly folder
    note_folder : Note folder dir
    start : Start date
    end : End date
    date_format : Date format for folder names
    '''
    note_folder.mkdir(exist_ok=True)
    weekly_folder = note_folder / f'{start.strftime(date_format)}_{end.strftime(date_format)}'
    weekly_folder.mkdir(exist_ok=True)
    return weekly_folder

def ensure_daily_file(weekly_folder: Path, today: date, date_format: str, sections: List[dict]) -> Path:
    '''
    Ensure daily file exists
    weekly_folder : Folder for week
    today : Todays date
    date_format : Date format for folder names
    sections: File sections
    '''
    day_file = weekly_folder / f'{today.strftime(date_format)}.md'
    if day_file.exists():
        return day_file
    text_contents = f'# {today.strftime(date_format)}\n'
    for section in sections:
        text_contents += f'\n## {section.title}\n{section.contents}\n'
    day_file.write_text(text_contents)
    return day_file

@click.group()
@click.option('-c', '--config-file', default=CONFIG_DEFAULT, show_default=True,
              type=click.Path(file_okay=True, dir_okay=False, exists=False))
@click.option('-n', '--note-folder',
              type=click.Path(file_okay=False, dir_okay=True, exists=False))
@click.option('-df', '--date-format')
@click.pass_context
def main(context: click.Context, config_file: str, note_folder: str, date_format: str):
    '''
    Main cli runner
    '''
    # Load config options
    config = {}
    if config_file.exists():
        config = parse_config(str(config_file))
    config = get_config_options(config, note_folder, date_format)
    context.obj = {
        'config': config,
    }

@main.command('ready-file')
@click.pass_context
def ready_file(context: click.Context):
    '''
    Ready the daily note file
    '''
    # Get date basics
    today = date.today()
    start = get_start_of_week(today)
    end = get_end_of_week(today)
    # Get folder and file ready
    weekly_folder = create_weekly_folder(context.obj['config']['note_folder'], start, end, context.obj['config']['date_format'])
    day_file = ensure_daily_file(weekly_folder, today, context.obj['config']['date_format'], context.obj['config']['sections'])
    click.echo(f'Created note file {day_file}')

@main.command('rollup')
@click.option('-rn', '--rollup-name', default='summary.md', show_default=True)
@click.option('-t', '--title')
@click.argument('file_dir', type=click.Path(file_okay=False, dir_okay=True, exists=True))
@click.pass_context
def rollup(context: click.Context, file_dir: str, title, rollup_name: str):
    '''
    Rollup daily note files
    '''
    file_dir = Path(file_dir)
    title = title or f'Summary | {file_dir.name.replace("_", " -> ")}'
    markdown_sections = []
    for path in list_markdown_files(file_dir):
        markdown_sections.append(generate_markdown_sections(path.read_text()))
    combos = combine_markdown_sections(markdown_sections, context.obj['config']['rollup_sections'])
    new_document = MarkdownSection(title, '')
    for section in combos:
        section.level = 2
        new_document.add_section(section)
    new_path = file_dir / rollup_name
    new_path.write_text(markdown_section_output(new_document))
    click.echo(f'Rollup data written to file {new_path}')

if __name__ == '__main__':
    main(obj={}) # pylint:disable=no-value-for-parameter

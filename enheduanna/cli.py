from datetime import date
from pathlib import Path
from typing import List

import click
from pyaml_env import parse_config
from pydantic import ValidationError

from enheduanna.types.markdown_file import MarkdownFile
from enheduanna.types.markdown_section import MarkdownSection

from enheduanna.utils.days import get_end_of_week, get_start_of_week
from enheduanna.utils.files import list_markdown_files, find_last_markdown_file
from enheduanna.utils.markdown import section_generate_from_json
from enheduanna.utils.markdown import rollup_section_generate_from_json
from enheduanna.utils.markdown import generate_markdown_rollup

class ConfigException(Exception):
    '''
    Generic Exception for config errors
    '''

CONFIG_DEFAULT = Path.home() / '.enheduanna.yml'
FOLDER_DEFAULT = Path.home() / 'Notes'
DOCUMENT_DEFAULT = Path.home() / 'Documents'
DATE_FORMAT_DEFAULT = '%Y-%m-%d'

SECTIONS_DEFAULT = [
    {
        'title': 'Work Done',
        'contents': '- ',
        'level': 2,
    },
    {
        'title': 'Meetings',
        'contents': '| Time | Meeting Name |\n| ---- | ------------ |\n| | |',
        'level': 2,
    },
    {
        'title': 'Follow Ups',
        'contents': '- ',
        'level': 2,
        'carryover': True,
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
        'level': 2,
    },
]

def get_config_options(config: dict) -> dict:
    '''
    Get config options from config file and cli
    config : Config dictionary
    '''
    config['note_folder'] = Path(config.get('note_folder', FOLDER_DEFAULT))
    config['date_format'] = config.get('date_format', DATE_FORMAT_DEFAULT)
    config['document_folder'] = Path(config.get('document_folder', DOCUMENT_DEFAULT))

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

def ensure_daily_file(weekly_folder: Path, today: date, date_format: str, new_sections: List[MarkdownSection],
                      last_markdown_file: MarkdownFile) -> Path:
    '''
    Ensure daily file exists
    weekly_folder : Folder for week
    today : Todays date
    date_format : Date format for folder names
    new_sections: Markdown Sections for new file
    last_markdown_file : Last created markdown file
    '''
    day_file = weekly_folder / f'{today.strftime(date_format)}.md'
    if day_file.exists():
        return day_file
    markdown_contents = MarkdownSection(today.strftime(date_format), '')
    for section in new_sections:
        # Carry over existing section from last file if applicable
        if last_markdown_file and section.carryover:
            existing_section = last_markdown_file.root_section.remove_section(section.title)
            if existing_section:
                markdown_contents.add_section(existing_section)
                last_markdown_file.write()
                continue
        markdown_contents.add_section(section)
    day_file.write_text(markdown_contents.write())
    return day_file

@click.group()
@click.option('-c', '--config-file', default=CONFIG_DEFAULT, show_default=True,
              type=click.Path(file_okay=True, dir_okay=False, exists=False))
@click.pass_context
def main(context: click.Context, config_file: str):
    '''
    Enheduanna CLI Runner
    '''
    # Load config options
    config = {}
    config_file = Path(config_file)
    if config_file.exists():
        config = parse_config(str(config_file))
    config = get_config_options(config)
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
    # Find last file, see if it has any carryover sections
    last_file = find_last_markdown_file(context.obj['config']['note_folder'])
    if last_file:
        last_file = MarkdownFile.from_file(last_file)
    # Get folder and file ready
    weekly_folder = create_weekly_folder(context.obj['config']['note_folder'], start, end, context.obj['config']['date_format'])
    day_file = ensure_daily_file(weekly_folder, today, context.obj['config']['date_format'], context.obj['config']['sections'], last_file)
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
    markdown_files = []
    for path in list_markdown_files(file_dir):
        markdown_files.append(MarkdownFile.from_file(path))
    # Ignore sections set automatically but not in rollup
    ignore_sections = set(i.title for i in context.obj['config']['sections']) - set([i.title for i in context.obj['config']['rollup_sections']]) #pylint:disable=consider-using-set-comprehension
    combos, documents = generate_markdown_rollup(markdown_files, context.obj['config']['rollup_sections'], ignore_sections)
    new_document = MarkdownSection(title, '')
    for section in combos:
        section.level = 2
        new_document.add_section(section)
    new_path = file_dir / rollup_name
    new_path.write_text(new_document.write())
    click.echo(f'Rollup data written to file {new_path}')
    for document in documents:
        new_path = context.obj['config']['document_folder'] / f'{document.title}.md'
        new_file = MarkdownFile(new_path, document)
        new_file.write()
        click.echo(f'Writing document to file {new_path}')

if __name__ == '__main__':
    main(obj={}) # pylint:disable=no-value-for-parameter

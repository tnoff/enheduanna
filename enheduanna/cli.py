from datetime import date, timedelta
from pathlib import Path
from typing import List

import click
from pyaml_env import parse_config

CONFIG_DEFAULT = Path.home() / '.enheduanna.yml'
FOLDER_DEFAULT = Path.home() / 'Notes'
DATE_FORMAT_DEFAULT = '%Y-%m-%d'
SECTIONS_DEFAULT = [
    {
        'title': 'Work Done',
        'contents': '',
    },
    {
        'title': 'Meetings',
        'contents': '| Time | Meeting Name |\n| ---- | ------------ |\n| | |\n',
    },
    {
        'title': 'Follow Ups',
        'contents': '',
    },
    {
        'title': 'Scratch',
        'contents': '',
    }
]


def get_start_of_week(day: date) -> date:
    '''
    Get start of week
    '''
    while True:
        if day.weekday() == 0:
            return day
        day = day - timedelta(days=1)

def get_end_of_week(day: date) -> date:
    '''
    Get end of week
    '''
    while True:
        if day.weekday() == 6:
            return day
        day = day + timedelta(days=1)

def get_config_options(config: dict, note_folder: Path, date_format: str) -> dict:
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
    config['sections'] = config.get('sections', SECTIONS_DEFAULT)
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
        text_contents += f'\n## {section["title"]}\n{section['contents']}'
    day_file.write_text(text_contents)
    return day_file

@click.group()
@click.option('-c', '--config-file', default=CONFIG_DEFAULT, show_default=True,
              type=click.Path(file_okay=True, dir_okay=False, exists=False))
@click.option('-n', '--note-folder',
              type=click.Path(file_okay=False, dir_okay=True, exists=False))
@click.option('-df', '--date-format')
@click.pass_context
def main(context: click.Context, config_file: Path, note_folder: Path, date_format: str):
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
    # Get date basics
    today = date.today()
    start = get_start_of_week(today)
    end = get_end_of_week(today)
    # Get folder and file ready
    weekly_folder = create_weekly_folder(context.obj['config']['note_folder'], start, end, context.obj['config']['date_format'])
    day_file = ensure_daily_file(weekly_folder, today, context.obj['config']['date_format'], context.obj['config']['sections'])
    click.echo(f'Created note file {day_file}')

if __name__ == '__main__':
    main(obj={}) # pylint:disable=no-value-for-parameter

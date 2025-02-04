from datetime import date
from tempfile import TemporaryDirectory

from click.testing import CliRunner
from freezegun import freeze_time
from pathlib import Path

from enheduanna.cli import FOLDER_DEFAULT, DATE_FORMAT_DEFAULT, SECTIONS_DEFAULT
from enheduanna.cli import get_start_of_week, get_end_of_week
from enheduanna.cli import get_config_options
from enheduanna.cli import create_weekly_folder
from enheduanna.cli import ensure_daily_file
from enheduanna.cli import main

def test_week_functions():
    today = date(2025, 2, 2)
    assert get_start_of_week(today) == date(2025, 1, 27)
    assert get_end_of_week(today) == date(2025, 2, 2)

def test_get_config_options():
    result = get_config_options({}, None, None)
    assert result['note_folder'] == FOLDER_DEFAULT
    assert result['date_format'] == DATE_FORMAT_DEFAULT

    result = get_config_options({
        'note_folder': '/home/foo/bar',
        'date_format': '%Y_%m_%d'
    }, None, None)
    assert str(result['note_folder']) == '/home/foo/bar'
    assert result['date_format'] == '%Y_%m_%d'

    result = get_config_options({
        'note_folder': '/home/foo/bar',
        'date_format': '%Y_%m_%d'
    }, '/home/foo/bar2', '%d-%m-%Y')

    assert str(result['note_folder']) == '/home/foo/bar2'
    assert str(result['date_format']) == '%d-%m-%Y'

def test_create_weekly_folder():
    with TemporaryDirectory() as tmpdir:
        start = date(2025, 1, 27)
        end = date(2025, 2, 2)
        result = create_weekly_folder(Path(tmpdir), start, end, '%Y-%m-%d')
        assert str(result) == str(Path(tmpdir) / '2025-01-27_2025-02-02')

def test_ensure_daily_file():
    with TemporaryDirectory() as tmpdir:
        today = date(2025, 2, 2)
        result = ensure_daily_file(Path(tmpdir), today, '%Y-%m-%d', SECTIONS_DEFAULT)
        assert str(result) == f'{tmpdir}/2025-02-02.md'
        result_contents = Path(result).read_text()
        assert result_contents == '# 2025-02-02\n\n## Work Done\n\n## Meetings\n| Time | Meeting Name |\n| ---- | ------------ |\n| | |\n\n## Follow Ups\n\n## Scratch\n'

@freeze_time('2024-12-01 12:00:00', tz_offset=0)
def test_ready_file_cli():
    with TemporaryDirectory() as tmpdir:
        runner = CliRunner()
        result = runner.invoke(main, ['-n', tmpdir, 'ready-file'])
        assert result.output == f'Created note file {tmpdir}/2024-11-25_2024-12-01/2024-12-01.md\n'

@freeze_time('2024-12-01 12:00:00', tz_offset=0)
def test_ready_file_cli_override_date_format():
    with TemporaryDirectory() as tmpdir:
        runner = CliRunner()
        result = runner.invoke(main, ['-n', tmpdir, '-df', '%d-%m-%Y', 'ready-file'])
        assert result.output == f'Created note file {tmpdir}/25-11-2024_01-12-2024/01-12-2024.md\n'

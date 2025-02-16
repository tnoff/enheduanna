from datetime import date
import json
from tempfile import TemporaryDirectory, NamedTemporaryFile

from click.testing import CliRunner
from freezegun import freeze_time
from pathlib import Path
from pytest import raises

from enheduanna.cli import ConfigException
from enheduanna.cli import FOLDER_DEFAULT, DATE_FORMAT_DEFAULT, SECTIONS_DEFAULT
from enheduanna.cli import get_start_of_week, get_end_of_week
from enheduanna.cli import get_config_options
from enheduanna.cli import create_weekly_folder
from enheduanna.cli import ensure_daily_file
from enheduanna.cli import main

from enheduanna.utils.markdown import section_generate_from_json

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

def test_validation_of_section_schema():
    with raises(ConfigException) as e:
        get_config_options({
            'sections': 'foo'
        }, None, None)
    assert 'Invalid section config given' in str(e.value)
    with raises(ConfigException) as e:
        get_config_options({
            'sections': [
                {
                    'foo': 'bar',
                    'title': 'bar',
                }
            ]
        }, None, None)
    assert 'Invalid section config given' in str(e.value)

def test_validation_rollup_sections():
    with raises(ConfigException) as e:
        get_config_options({
            'rollup_sections': 'foo'
        }, None, None)
    assert 'Invalid rollup sections given' in str(e.value)

def test_create_weekly_folder():
    with TemporaryDirectory() as tmpdir:
        start = date(2025, 1, 27)
        end = date(2025, 2, 2)
        result = create_weekly_folder(Path(tmpdir), start, end, '%Y-%m-%d')
        assert str(result) == str(Path(tmpdir) / '2025-01-27_2025-02-02')

def test_ensure_daily_file():
    with TemporaryDirectory() as tmpdir:
        today = date(2025, 2, 2)
        result = ensure_daily_file(Path(tmpdir), today, '%Y-%m-%d', section_generate_from_json(SECTIONS_DEFAULT))
        assert str(result) == f'{tmpdir}/2025-02-02.md'
        result_contents = Path(result).read_text()
        print(result_contents)
        assert result_contents == '# 2025-02-02\n\n## Work Done\n\n- \n\n## Meetings\n\n| Time | Meeting Name |\n| ---- | ------------ |\n| | |\n\n## Follow Ups\n\n- \n\n## Scratch\n'

@freeze_time('2024-12-01 12:00:00', tz_offset=0)
def test_ready_file_cli():
    with TemporaryDirectory() as tmpdir:
        runner = CliRunner()
        result = runner.invoke(main, ['-n', tmpdir, 'ready-file'])
        print(result.exception)
        assert result.output == f'Created note file {tmpdir}/2024-11-25_2024-12-01/2024-12-01.md\n'

@freeze_time('2024-12-01 12:00:00', tz_offset=0)
def test_ready_file_cli_override_date_format():
    with TemporaryDirectory() as tmpdir:
        runner = CliRunner()
        result = runner.invoke(main, ['-n', tmpdir, '-df', '%d-%m-%Y', 'ready-file'])
        assert result.output == f'Created note file {tmpdir}/25-11-2024_01-12-2024/01-12-2024.md\n'

def test_rollup():
    file1_text = '''# 2025-01-01

## Work Done

- I did this ticket today (XYZ-234)
- Another random ticket I did (ASF-123)
- Some random task

## Random Section Not tracked

This wont show up in the rollup

## Follow Ups

- Random follow up for today
'''
    file2_text = '''# 2025-01-02

## Work Done

- Another update on that ticket (XYZ-234)

## Follow Ups

- Dont forget to do this other thing
'''

    with TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir) / '2025-02-10_2025-02-16'
        dir_path.mkdir()
        runner = CliRunner()
        with NamedTemporaryFile(dir=dir_path, prefix='abc', suffix='.md') as file1:
            path1 = Path(file1.name)
            path1.write_text(file1_text)
            with NamedTemporaryFile(dir=dir_path, prefix='xyz', suffix='.md') as file2:
                path2 = Path(file2.name)
                path2.write_text(file2_text)
                runner.invoke(main, ['-n', tmpdir, 'rollup', str(dir_path)])
                expected_path = dir_path / 'summary.md'
                assert expected_path.exists()
                text = expected_path.read_text()
                assert text == f'# Summary | 2025-02-10 -> 2025-02-16\n\n## Work Done\n\n- I did this ticket today (XYZ-234)\n- Another update on that ticket (XYZ-234)\n\n- Another random ticket I did (ASF-123)\n\n- Some random task\n\n## Follow Ups\n\n- Random follow up for today\n- Dont forget to do this other thing\n'


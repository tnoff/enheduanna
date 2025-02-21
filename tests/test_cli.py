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

from enheduanna.types.markdown_file import MarkdownFile
from enheduanna.utils.markdown import section_generate_from_json

def test_week_functions():
    today = date(2025, 2, 2)
    assert get_start_of_week(today) == date(2025, 1, 27)
    assert get_end_of_week(today) == date(2025, 2, 2)

def test_get_config_options():
    result = get_config_options({})
    assert result['note_folder'] == FOLDER_DEFAULT
    assert result['date_format'] == DATE_FORMAT_DEFAULT

    result = get_config_options({
        'note_folder': '/home/foo/bar',
        'date_format': '%Y_%m_%d'
    })
    assert str(result['note_folder']) == '/home/foo/bar'
    assert result['date_format'] == '%Y_%m_%d'

def test_validation_of_section_schema():
    with raises(ConfigException) as e:
        get_config_options({
            'sections': 'foo'
        })
    assert 'Invalid section config given' in str(e.value)
    with raises(ConfigException) as e:
        get_config_options({
            'sections': [
                {
                    'foo': 'bar',
                    'title': 'bar',
                }
            ]
        })
    assert 'Invalid section config given' in str(e.value)

def test_validation_rollup_sections():
    with raises(ConfigException) as e:
        get_config_options({
            'rollup_sections': 'foo'
        })
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
        result = ensure_daily_file(Path(tmpdir), today, '%Y-%m-%d', section_generate_from_json(SECTIONS_DEFAULT), None)
        assert str(result) == f'{tmpdir}/2025-02-02.md'
        result_contents = Path(result).read_text()
        assert result_contents == '# 2025-02-02\n\n## Work Done\n\n- \n\n## Meetings\n\n| Time | Meeting Name |\n| ---- | ------------ |\n| | |\n\n## Follow Ups\n\n- \n\n## Scratch\n'

def test_ensure_daily_file_with_carryover():
    file1_text = '''# 2025-02-16

## Dummy Section

Make sure this is still there afterward

## Follow Ups

- Carry over this followup to the next day
'''
    with TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        weekly_dir = dir_path / '2025-02-10_2025-02-16'
        weekly_dir.mkdir()
        last_daily_path = weekly_dir / '2025-02-16'
        last_daily_path.write_text(file1_text)
        last_daily_file = MarkdownFile.from_file(last_daily_path)
        today = date(2025, 2, 17)
        result = ensure_daily_file(Path(tmpdir), today, '%Y-%m-%d', section_generate_from_json(SECTIONS_DEFAULT), last_daily_file)
        assert result.read_text() == '# 2025-02-17\n\n## Work Done\n\n- \n\n## Meetings\n\n| Time | Meeting Name |\n| ---- | ------------ |\n| | |\n\n## Follow Ups\n\n- Carry over this followup to the next day\n\n## Scratch\n'
        assert last_daily_path.read_text() == '# 2025-02-16\n\n## Dummy Section\n\nMake sure this is still there afterward\n'

@freeze_time('2025-12-01 12:00:00', tz_offset=0)
def test_ready_file_cli():
        runner = CliRunner()
        result = runner.invoke(main, ['-n', tmpdir, 'ready-file'])
        assert result.output == f'Created note file {tmpdir}/2024-11-25_2024-12-01/2024-12-01.md\n'

@freeze_time('2025-02-17 12:00:00', tz_offset=0)
def test_ready_file_cli_with_carryover():
    file1_text = '''# 2025-02-16

## Dummy Section

Make sure this is still there afterward

## Follow Ups

- Carry over this followup to the next day
'''
    with TemporaryDirectory() as tmpdir:
        with NamedTemporaryFile() as tmp_config:
            config_path = Path(tmp_config.name)
            config_path.write_text(f'---\nnote_folder: {tmpdir}\n')
            dir_path = Path(tmpdir)
            weekly_dir = dir_path / '2025-02-10_2025-02-16'
            weekly_dir.mkdir()
            last_daily_path = weekly_dir / '2025-02-16'
            last_daily_path.write_text(file1_text)
            runner = CliRunner()
            result = runner.invoke(main, ['-c', tmp_config.name, 'ready-file'])
            assert result.output == f'Created note file {tmpdir}/2025-02-17_2025-02-23/2025-02-17.md\n'

@freeze_time('2024-12-01 12:00:00', tz_offset=0)
def test_ready_file_cli():
    with TemporaryDirectory() as tmpdir:
        with NamedTemporaryFile() as tmp_config:
            config_path = Path(tmp_config.name)
            config_path.write_text(f'---\nnote_folder: {tmpdir}\n')
            runner = CliRunner()
            result = runner.invoke(main, ['-c', tmp_config.name, 'ready-file'])
            assert result.output == f'Created note file {tmpdir}/2024-11-25_2024-12-01/2024-12-01.md\n'

def test_rollup():
    file1_text = '''# 2025-02-10

## Work Done

- I did this ticket today (XYZ-234)
- Another random ticket I did (ASF-123)
- Some random task

## Follow Ups

- This should get ignored in the rollup

## Random Non Rolloup Section

This will be generated as a document section
'''
    file2_text = '''# 2025-02-11

## Work Done

- Another update on that ticket (XYZ-234)
'''
    with TemporaryDirectory() as tmpdir:
        with TemporaryDirectory() as doc_dir:
            with NamedTemporaryFile() as tmp_config:
                config_path = Path(tmp_config.name)
                config_path.write_text(f'---\nnote_folder: {tmpdir}\ndocument_folder: {doc_dir}')
                dir_path = Path(tmpdir) / '2025-02-10_2025-02-16'
                dir_path.mkdir()
                file1 = dir_path / '2025-02-10.md'
                file1.write_text(file1_text)
                file2 = dir_path / '2025-02-11.md'
                file2.write_text(file2_text)
                runner = CliRunner()
                result = runner.invoke(main, ['-c', str(tmp_config.name), 'rollup', str(dir_path)])
                expected_path = dir_path / 'summary.md'
                assert 'Rollup data written to file' in result.output
                assert 'Writing document to file' in result.output
                assert expected_path.exists()
                text = expected_path.read_text()
                assert text == f'# Summary | 2025-02-10 -> 2025-02-16\n\n## Work Done\n\n- I did this ticket today (XYZ-234)\n- Another update on that ticket (XYZ-234)\n\n- Another random ticket I did (ASF-123)\n\n- Some random task\n'
                expected_doc = Path(doc_dir) / '2025-02-10 Random Non Rolloup Section.md'
                assert expected_doc.exists()
                assert expected_doc.read_text() == '# 2025-02-10 Random Non Rolloup Section\n\nThis will be generated as a document section\n'

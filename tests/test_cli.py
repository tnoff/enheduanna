from datetime import date
import json
from tempfile import TemporaryDirectory, NamedTemporaryFile

from click.testing import CliRunner
from freezegun import freeze_time
from pathlib import Path


from enheduanna.cli import main


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
            config_path.write_text(f'---\nfile:\n  note_folder: {tmpdir}\n')
            dir_path = Path(tmpdir)
            weekly_dir = dir_path / '2025-02-10_2025-02-16'
            weekly_dir.mkdir()
            last_daily_path = weekly_dir / '2025-02-16'
            last_daily_path.write_text(file1_text)
            runner = CliRunner()
            result = runner.invoke(main, ['-c', tmp_config.name, 'file', 'ready'])
            print(result.output)
            print(result.exception)
            assert result.output == f'Created note file {tmpdir}/2025-02-17_2025-02-23/2025-02-17.md\n'

@freeze_time('2024-12-01 12:00:00', tz_offset=0)
def test_ready_file_cli():
    with TemporaryDirectory() as tmpdir:
        with NamedTemporaryFile() as tmp_config:
            config_path = Path(tmp_config.name)
            config_path.write_text(f'---\nfile:\n  note_folder: {tmpdir}\n')
            runner = CliRunner()
            result = runner.invoke(main, ['-c', tmp_config.name, 'file', 'ready'])
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
                config_path.write_text(f'---\nfile:\n  note_folder: {tmpdir}\n  document_folder: {doc_dir}')
                dir_path = Path(tmpdir) / '2025-02-10_2025-02-16'
                dir_path.mkdir()
                file1 = dir_path / '2025-02-10.md'
                file1.write_text(file1_text)
                file2 = dir_path / '2025-02-11.md'
                file2.write_text(file2_text)
                runner = CliRunner()
                result = runner.invoke(main, ['-c', str(tmp_config.name), 'file', 'rollup', str(dir_path)])
                expected_path = dir_path / 'summary.md'
                assert 'Rollup data written to file' in result.output
                assert 'Writing document to file' in result.output
                assert expected_path.exists()
                text = expected_path.read_text()
                assert text == f'# Summary | 2025-02-10 -> 2025-02-16\n\n## Work Done\n\n- I did this ticket today (XYZ-234)\n- Another update on that ticket (XYZ-234)\n\n- Another random ticket I did (ASF-123)\n\n- Some random task\n'
                expected_doc = Path(doc_dir) / '2025-02-10 Random Non Rolloup Section.md'
                assert expected_doc.exists()
                assert expected_doc.read_text() == '# 2025-02-10 Random Non Rolloup Section\n\nThis will be generated as a document section\n'

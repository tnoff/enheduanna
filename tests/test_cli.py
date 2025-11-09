from contextlib import contextmanager
from distutils.dir_util import copy_tree
from json import dumps
from tempfile import TemporaryDirectory, NamedTemporaryFile

from click.testing import CliRunner
from freezegun import freeze_time
from pathlib import Path
from pydantic import RootModel
from yaml import dump

from enheduanna.cli import main

from enheduanna.types.config import Config
from enheduanna.types.config.file import FileConfig

DATA_PATH = Path(__file__).parent / 'data'

@contextmanager
def temp_config():
    with NamedTemporaryFile() as tmp_config:
        config_path = Path(tmp_config.name)
        with TemporaryDirectory() as note_dir:
            with TemporaryDirectory() as doc_dir:
                file_config = FileConfig(entries_directory=note_dir, document_directory=doc_dir)
                config = Config(file_config, {})
                config_path.write_text(dump(RootModel[Config](config).model_dump_json()))
                yield config_path, config

@freeze_time('2025-03-01 12:00:00', tz_offset=0)
def test_new_entry():
    data_dir = DATA_PATH / '2025-02-24_2025-03-02'
    with temp_config() as (config_file, config):
        copy_tree(data_dir, config.file.entries_directory / '2025-02-24_2025-03-02')
        runner = CliRunner()
        result = runner.invoke(main, ['-c', config_file, 'new-entry'])
        assert result.output == f'Created entry file {config.file.entries_directory}/2025-02-24_2025-03-02/2025-03-01.md\n'
        expected_path = config.file.entries_directory / '2025-02-24_2025-03-02' / '2025-03-01.md'
        assert expected_path.exists()
        assert expected_path.read_text() == '# 2025-03-01\n\n## Work Done\n\n- \n\n## Meetings\n\n| Time | Meeting Name |\n| ---- | ------------ |\n| | |\n\n## Follow Ups\n\n### Short Term\n\n- Grab that report for the boss\n- Email back Jon\n\n### Long Term\n\n- Remind Jon that he knows nothing\n\n## Scratch\n\n- \n'

        previous_file = config.file.entries_directory / '2025-02-24_2025-03-02' / '2025-02-28.md'
        assert previous_file.exists()
        assert previous_file.read_text() == '# 2025-02-28\n\n## Work Done\n\n- Doing some testing for customer fix (ABC-1234)\n- Helping Arya fix up her test suite\n- Doing self-reviews for the year\n\n## Meetings\n\n| Time | Summary |\n| ---- | ------- |\n| 0900 -> 1000 | Standup |\n| 1300 -> 1500 | Sync w/ Boss |\n\n## Scratch\n\nRandom testing steps\n```\nssh ubuntu@1.2.3.4\nsudo reboot\n```\n'

@freeze_time('2025-03-01 12:00:00', tz_offset=0)
def test_collate():
    data_dir = DATA_PATH / '2025-02-24_2025-03-02'
    with temp_config() as (config_file, config):
        copy_tree(data_dir, config.file.entries_directory / '2025-02-24_2025-03-02')
        runner = CliRunner()
        result = runner.invoke(main, ['-c', config_file, 'collate', str(config.file.entries_directory / '2025-02-24_2025-03-02')])

        assert result.output == f'Collation data written to file {config.file.entries_directory}/2025-02-24_2025-03-02/summary.md\nWriting document to file {config.file.document_directory}/2025-02-27 How to Answer Question.md\nWriting document to file {config.file.document_directory}/2025-02-27 Another Specific Question.md\nCleaning up files in dir {config.file.entries_directory}/2025-02-24_2025-03-02\n'
        expected_summary = config.file.entries_directory / '2025-02-24_2025-03-02' / 'summary.md'
        assert expected_summary.exists()
        assert expected_summary.read_text() == '# Summary | 2025-02-24 -> 2025-03-02\n\n## Work Done\n\n- Writing up customer support (ABC-1234)\n- Doing some testing for customer fix (ABC-1234)\n\n- Helping Arya fix up her test suite\n- Doing self-reviews for the year\n'

        expected_doc1 = config.file.document_directory / '2025-02-27 How to Answer Question.md'
        assert expected_doc1.exists()
        assert expected_doc1.read_text() == '# 2025-02-27 How to Answer Question\n\nHow to answer a specific question Sansa asked\nWriting this down for later\n```\nssh ubuntu@foo\nsudo /usr/lib/bin/execute.sh\n```\n'

        expected_doc2 = config.file.document_directory / '2025-02-27 Another Specific Question.md'
        assert expected_doc2.exists()
        assert expected_doc2.read_text() == '# 2025-02-27 Another Specific Question\n\nHow to answer another specific question\nThis can be rolled up into a runbook later\n\n## Another point\n\nThis is another point that should go in the same runbook doc\n'

        scratch_file = config.file.entries_directory / '2025-02-24_2025-03-02' / '2025-02-27.md'
        assert scratch_file.exists()
        assert scratch_file.read_text() == '# 2025-02-27\n\n## Work Done\n\n- Writing up customer support (ABC-1234)\n\n## Meetings\n\n| Time | Summary |\n| ---- | ------- |\n| 0900 -> 1000 | Standup |\n| 1300 -> 1500 | Sync w/ Boss |\n'

@freeze_time('2025-03-01 12:00:00', tz_offset=0)
def test_merge():
    # Simulate documentation files that were extracted from previous collate operations
    with temp_config() as (config_file, config):
        runner = CliRunner()

        # Create sample documentation files (like those extracted from collate)
        doc1_path = config.file.document_directory / '2025-02-10 How to Deploy API.md'
        doc1_content = '''# 2025-02-10 How to Deploy API

## Prerequisites

- SSH access to production servers
- Deploy keys configured

## Deployment Steps

1. Run the build script: `./build.sh`
2. Deploy to staging: `./deploy.sh staging`
3. Run smoke tests
'''
        doc1_path.write_text(doc1_content)

        doc2_path = config.file.document_directory / '2025-02-15 How to Deploy API.md'
        doc2_content = '''# 2025-02-15 How to Deploy API

## Prerequisites

- VPN connection active

## Deployment Steps

4. Deploy to production: `./deploy.sh prod`
5. Monitor logs for errors

## Rollback Procedure

If deployment fails:
- Run: `./rollback.sh`
- Verify services are healthy
'''
        doc2_path.write_text(doc2_content)

        doc3_path = config.file.document_directory / '2025-02-20 Database Migration Guide.md'
        doc3_content = '''# 2025-02-20 Database Migration Guide

## Prerequisites

- Database backup completed
- Maintenance window scheduled

## Migration Steps

1. Put app in maintenance mode
2. Run migration: `python manage.py migrate`
3. Verify data integrity
'''
        doc3_path.write_text(doc3_content)

        # Now merge the documentation files into a single runbook
        output_file = config.file.document_directory / 'complete-operations-runbook.md'
        result = runner.invoke(main, ['-c', config_file, 'merge',
                                     str(config.file.document_directory),
                                     str(output_file),
                                     '-t', 'Complete Operations Runbook'])

        assert result.output == f'Merged data written to file {output_file}\n'
        assert output_file.exists()

        content = output_file.read_text()

        # Verify the merged document has the custom title
        assert '# Complete Operations Runbook' in content

        # Verify each file becomes a level 2 section
        assert '## 2025-02-10 How to Deploy API' in content
        assert '## 2025-02-15 How to Deploy API' in content
        assert '## 2025-02-20 Database Migration Guide' in content

        # Verify subsections are at level 3
        assert '### Prerequisites' in content
        assert 'SSH access to production servers' in content
        assert 'VPN connection active' in content
        assert 'Database backup completed' in content

        # Verify Deployment Steps section exists
        assert '### Deployment Steps' in content
        assert './build.sh' in content
        assert './deploy.sh prod' in content

        # Verify Rollback Procedure section exists
        assert '### Rollback Procedure' in content
        assert './rollback.sh' in content

        # Verify Migration Steps section exists
        assert '### Migration Steps' in content
        assert 'python manage.py migrate' in content
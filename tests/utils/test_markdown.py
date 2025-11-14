from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile

from pydantic_core._pydantic_core import ValidationError
from pytest import raises

from enheduanna.types.markdown.markdown_file import MarkdownFile
from enheduanna.types.markdown.markdown_section import MarkdownSection
from enheduanna.types.markdown.collate_section import CollateSection
from enheduanna.utils.markdown import section_generate_from_json
from enheduanna.utils.markdown import collate_section_generate_from_json
from enheduanna.utils.markdown import generate_markdown_collation
from enheduanna.utils.markdown import generate_markdown_merge
from enheduanna.utils.markdown import remove_empty_sections


def test_validation_of_section_schema():
    with raises(ValidationError) as e:
        section_generate_from_json({'sections': 'foo'})
    assert '1 validation error for MarkdownSection' in str(e.value)
    with raises(ValidationError) as e:
        section_generate_from_json([
                {
                    'foo': 'bar',
                    'title': 'bar',
                }
            ])
    assert '1 validation error for MarkdownSection' in str(e.value)
    valid = section_generate_from_json([{"title": "foo", "contents": "bar"}])
    assert valid[0].title == "foo"
    assert valid[0].contents == "bar"

def test_validation_of_collate_schema():
    valid = collate_section_generate_from_json([{"title": "foo"}])
    assert valid[0].title == "foo"

def test_combine_markdown_sections():
    ms1 = MarkdownSection('2025-02-10', '')
    ms1.add_section(MarkdownSection('Work Done', '- Some example ticket work (ABC-1234)\nRandom input', level=2))
    ms1.add_section(MarkdownSection('Follow Ups', '- Some example followup', level=2))
    ms1.add_section(MarkdownSection('Steps to Reboot Servers', 'dummy data', level=2))
    ms1.add_section(MarkdownSection('Notes From 1 on 1 with Cyrus', 'dummy data', level=2))

    ms2 = MarkdownSection('2025-02-11', '')
    ms2.add_section(MarkdownSection('Follow Ups', '- Another followup, different day', level=2))
    ms3 = MarkdownSection('Work Done', '- Follow Ups on Ticket (ABC-1234)', level=2)
    ms3.add_section(MarkdownSection('Easy Work', '- Work on ticket (ABC-1234)\n-Work on another ticket (XYZ-1234)', level=3))
    ms2.add_section(ms3)

    cs1 = CollateSection('Work Done', regex='\\((?P<ticket>[A-Za-z]+-[0-9]+)\\)', groupBy='ticket')

    with TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir) / '2025-02-10_2025-02-16'
        dir_path.mkdir()
        path1 = dir_path / '2025-02-10.md'
        path2 = dir_path / '2025-02-11.md'

        mf1 = MarkdownFile(path1, ms1)
        mf2 = MarkdownFile(path2, ms2)
        result, document = generate_markdown_collation([mf1, mf2], [cs1], ['Follow Ups'])
        assert len(result) == 1
        assert len(document) == 2
        assert result[0].title == 'Work Done'
        assert result[0].contents == '- Some example ticket work (ABC-1234)\n- Follow Ups on Ticket (ABC-1234)\n\nRandom input'
        assert result[0].sections[0].title == 'Easy Work'
        assert result[0].sections[0].contents == '- Work on ticket (ABC-1234)\n\n-Work on another ticket (XYZ-1234)'

        assert document[0].title == '2025-02-10 Steps to Reboot Servers'
        assert document[0].contents == 'dummy data'
        assert document[0].level == 1

        assert document[1].title == '2025-02-10 Notes From 1 on 1 with Cyrus'
        assert document[1].contents == 'dummy data'
        assert document[1].level == 1

        assert len(ms1.sections) == 2
        assert path1.read_text() == '# 2025-02-10\n\n## Work Done\n\n- Some example ticket work (ABC-1234)\nRandom input\n\n## Follow Ups\n\n- Some example followup\n'

def test_merge_markdown_sections():
    # Simulate documentation files that were extracted from collate command
    # These would typically be runbooks, HOWTOs, etc.
    doc1 = MarkdownSection('2025-02-10 How to Deploy API', '')
    doc1.add_section(MarkdownSection('Prerequisites', '- Access to prod environment\n- Deploy key', level=2))
    doc1.add_section(MarkdownSection('Steps', '1. Run build script\n2. Deploy to staging', level=2))

    doc2 = MarkdownSection('2025-02-15 How to Deploy API', '')
    doc2.add_section(MarkdownSection('Prerequisites', '- VPN connection', level=2))
    doc2.add_section(MarkdownSection('Steps', '3. Run smoke tests\n4. Deploy to production', level=2))
    doc2.add_section(MarkdownSection('Rollback', 'Use the rollback.sh script if needed', level=2))

    doc3 = MarkdownSection('2025-02-20 Database Migration Steps', '')
    doc3.add_section(MarkdownSection('Prerequisites', '- Database backup completed', level=2))
    doc3.add_section(MarkdownSection('Migration Process', '1. Stop app servers\n2. Run migration script', level=2))

    with TemporaryDirectory() as tmpdir:
        docs_dir = Path(tmpdir) / 'documentation'
        docs_dir.mkdir()
        path1 = docs_dir / '2025-02-10 How to Deploy API.md'
        path2 = docs_dir / '2025-02-15 How to Deploy API.md'
        path3 = docs_dir / '2025-02-20 Database Migration Steps.md'

        mf1 = MarkdownFile(path1, doc1)
        mf2 = MarkdownFile(path2, doc2)
        mf3 = MarkdownFile(path3, doc3)

        result = generate_markdown_merge([mf1, mf2, mf3], 'Combined Operations Runbook')

        assert result.title == 'Combined Operations Runbook'
        assert result.level == 1
        # Each file becomes a section
        assert len(result.sections) == 3

        # Check that files are at level 2
        deploy_api_1 = result.sections[0]
        deploy_api_2 = result.sections[1]
        migration_doc = result.sections[2]

        assert deploy_api_1.title == '2025-02-10 How to Deploy API'
        assert deploy_api_1.level == 2
        assert len(deploy_api_1.sections) == 2  # Prerequisites, Steps

        assert deploy_api_2.title == '2025-02-15 How to Deploy API'
        assert deploy_api_2.level == 2
        assert len(deploy_api_2.sections) == 3  # Prerequisites, Steps, Rollback

        assert migration_doc.title == '2025-02-20 Database Migration Steps'
        assert migration_doc.level == 2
        assert len(migration_doc.sections) == 2  # Prerequisites, Migration Process

        # Check that subsections are at level 3
        assert deploy_api_1.sections[0].level == 3
        assert deploy_api_1.sections[0].title == 'Prerequisites'
        assert '- Access to prod environment' in deploy_api_1.sections[0].contents

        assert deploy_api_2.sections[2].title == 'Rollback'
        assert deploy_api_2.sections[2].level == 3
        assert 'rollback.sh' in deploy_api_2.sections[2].contents

        assert migration_doc.sections[1].title == 'Migration Process'
        assert migration_doc.sections[1].level == 3
        assert 'Stop app servers' in migration_doc.sections[1].contents

def test_remove_sections():
    m = MarkdownSection('2025-03-01', '', level=1)
    m1 = MarkdownSection('Scratch', '-', level=2)
    m2 = MarkdownSection('Work Done', '', level=2)
    m21 = MarkdownSection('Easy Stuff', '- Got plenty of easy stuff', level=3)
    m3 = MarkdownSection('Empty with empty sub', '', level=2)
    m31 = MarkdownSection('Empty sub', '', level=3)
    m3.add_section(m31)
    m.add_section(m1)
    m2.add_section(m21)
    m.add_section(m2)
    m.add_section(m3)

    with NamedTemporaryFile() as tmp:
        path = Path(tmp.name)
        mf1 = MarkdownFile(path, m)
        remove_empty_sections([mf1])

        assert path.read_text() == '# 2025-03-01\n\n## Work Done\n\n### Easy Stuff\n\n- Got plenty of easy stuff\n'
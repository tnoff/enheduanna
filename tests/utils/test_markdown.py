from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic_core._pydantic_core import ValidationError
from pytest import raises

from enheduanna.types.markdown_file import MarkdownFile
from enheduanna.types.markdown_section import MarkdownSection
from enheduanna.types.rollup_section import RollupSection
from enheduanna.utils.markdown import section_generate_from_json
from enheduanna.utils.markdown import rollup_section_generate_from_json
from enheduanna.utils.markdown import generate_markdown_rollup


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

def test_validation_of_rollup_schema():
    valid = rollup_section_generate_from_json([{"title": "foo"}])
    assert valid[0].title == "foo"

def test_combine_markdown_sections():
    ms1 = MarkdownSection('2025-02-10', '')
    ms1.add_section(MarkdownSection('Work Done', '- Some example ticket work (ABC-1234)\nRandom input', level=2))
    ms1.add_section(MarkdownSection('Follow Ups', '- Some example followup', level=2))
    ms1.add_section(MarkdownSection('Steps to Reboot Servers', 'dummy data', level=2))

    ms2 = MarkdownSection('2025-02-11', '')
    ms2.add_section(MarkdownSection('Follow Ups', '- Another followup, different day', level=2))
    ms3 = MarkdownSection('Work Done', '- Follow Ups on Ticket (ABC-1234)', level=2)
    ms3.add_section(MarkdownSection('Easy Work', '- Work on ticket (ABC-1234)\n-Work on another ticket (XYZ-1234)', level=3))
    ms2.add_section(ms3)

    rs1 = RollupSection('Work Done', regex='\\((?P<ticket>[A-Za-z]+-[0-9]+)\\)', groupBy='ticket')

    with TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir) / '2025-02-10_2025-02-16'
        dir_path.mkdir()
        path1 = dir_path / '2025-02-10.md'
        path2 = dir_path / '2025-02-11.md'

        mf1 = MarkdownFile(path1, ms1)
        mf2 = MarkdownFile(path2, ms2)
        result, document = generate_markdown_rollup([mf1, mf2], [rs1], ['Follow Ups'])
        assert len(result) == 1
        assert len(document) == 1
        assert result[0].title == 'Work Done'
        assert result[0].contents == '- Some example ticket work (ABC-1234)\n- Follow Ups on Ticket (ABC-1234)\n\nRandom input'
        assert result[0].sections[0].title == 'Easy Work'
        assert result[0].sections[0].contents == '- Work on ticket (ABC-1234)\n\n-Work on another ticket (XYZ-1234)'

        assert document[0].title == '2025-02-10 Steps to Reboot Servers'
        assert document[0].contents == 'dummy data'
        assert document[0].level == 1

        assert len(ms1.sections) == 2
        assert path1.read_text() == '# 2025-02-10\n\n## Work Done\n\n- Some example ticket work (ABC-1234)\nRandom input\n\n## Follow Ups\n\n- Some example followup\n'

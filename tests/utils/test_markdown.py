from pydantic_core._pydantic_core import ValidationError
from pytest import raises

from enheduanna.types.markdown_section import MarkdownSection
from enheduanna.types.rollup_section import RollupSection
from enheduanna.utils.markdown import section_generate_from_json
from enheduanna.utils.markdown import rollup_section_generate_from_json
from enheduanna.utils.markdown import combine_markdown_sections


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
    ms1 = MarkdownSection('2025-01-01', '')
    ms1.add_section(MarkdownSection('Work Done', '- Some example ticket work (ABC-1234)\nRandom input', level=2))
    ms1.add_section(MarkdownSection('Follow Ups', '- Some example followup', level=2))
    ms1.add_section(MarkdownSection('Scratch', 'dummy data', level=2))

    ms2 = MarkdownSection('2025-02-02', '')
    ms2.add_section(MarkdownSection('Work Done', '- Same ticket, different update (ABC-1234)', level=2))
    ms2.add_section(MarkdownSection('Follow Ups', '- Another followup, different day', level=2))

    rs1 = RollupSection('Work Done', regex='\\((?P<ticket>[A-Za-z]+-[0-9]+)\\)', groupBy='ticket')
    rs2 = RollupSection('Follow Ups')
    result = combine_markdown_sections([ms1, ms2], [rs1, rs2])
    assert result[0].title == 'Work Done'
    assert result[0].contents == '- Some example ticket work (ABC-1234)\n- Same ticket, different update (ABC-1234)\n\nRandom input'
    assert result[1].title == 'Follow Ups'
    assert result[1].contents == '- Some example followup\n- Another followup, different day'

from pydantic_core._pydantic_core import ValidationError
from pytest import raises

from enheduanna.types.markdown_section import MarkdownSection
from enheduanna.types.rollup_section import RollupSection
from enheduanna.utils.markdown import section_generate_from_json
from enheduanna.utils.markdown import rollup_section_generate_from_json
from enheduanna.utils.markdown import generate_markdown_sections
from enheduanna.utils.markdown import combine_markdown_sections
from enheduanna.utils.markdown import markdown_section_output


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


def test_generate_markdown_sections():
    input_text = '''# 2025-01-01

Some example text for the day

## Work Done

- This is what I did today
- It was very neat
- I learned many things, fought many dragons

## Follow Ups

- Stuff I still need to do
- Hopefully I dont forget about it
- This is why we write it down'''
    result = generate_markdown_sections(input_text)
    assert result.title == '2025-01-01'
    assert result.contents == 'Some example text for the day'
    assert result.level == 1
    first_section = result.sections[0]
    assert first_section.title == 'Work Done'
    assert first_section.contents == '- This is what I did today\n- It was very neat\n- I learned many things, fought many dragons'
    assert first_section.level == 2
    second_section = result.sections[1]
    assert second_section.title == 'Follow Ups'
    assert second_section.contents == '- Stuff I still need to do\n- Hopefully I dont forget about it\n- This is why we write it down'
    assert second_section.level == 2

def test_generate_markdown_sections_with_nested():
    input_text = '''# 2025-01-01

Some example text for the day

## Work Done

- This is what I did today
- It was very neat
- I learned many things, fought many dragons

### Specific Nested Loop

These bits are nested on the 3rd loop'''
    result = generate_markdown_sections(input_text)
    assert result.title == '2025-01-01'
    assert result.contents == 'Some example text for the day'
    assert result.level == 1
    first_section = result.sections[0]
    assert first_section.title == 'Work Done'
    assert first_section.contents == '- This is what I did today\n- It was very neat\n- I learned many things, fought many dragons'
    assert first_section.level == 2
    nested_section = first_section.sections[0]
    assert nested_section.title == 'Specific Nested Loop'
    assert nested_section.contents == 'These bits are nested on the 3rd loop'
    assert nested_section.level == 3

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
    assert result[0].contents == '- Some example ticket work (ABC-1234)\n- Same ticket, different update (ABC-1234)\n\nRandom input\n'
    assert result[1].title == 'Follow Ups'
    assert result[1].contents == '- Some example followup\n- Another followup, different day\n'

def test_markdown_output():
    ms1 = MarkdownSection('2025-01-01', 'Some example contents')
    ms1.add_section(MarkdownSection('Stuffs Did', '-Did a thing\nDid another thing', level=2))
    ms2 = MarkdownSection('More Things', 'Some example stuff', level=2)
    ms2.add_section(MarkdownSection('Nested', 'More nested section', level=3))
    ms1.add_section(ms2)
    result = markdown_section_output(ms1)
    assert result == '# 2025-01-01\n\nSome example contents\n## Stuffs Did\n\n-Did a thing\nDid another thing\n\n## More Things\n\nSome example stuff\n### Nested\n\nMore nested section'

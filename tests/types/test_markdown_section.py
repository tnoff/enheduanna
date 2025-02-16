from enheduanna.types.markdown_section import MarkdownSection

def test_markdown_write():
    m = MarkdownSection('2025-02-16', 'generic contents')
    m.add_section(MarkdownSection('Sub-Section', '- Some generic contents in list', level=2))
    n = MarkdownSection('Another sub-section', 'Some generic stuff\nNot in list form', level=2)
    n.add_section(MarkdownSection('Another level in', '', level=3))
    m.add_section(n)
    result = m.write()
    assert result == '# 2025-02-16\n\ngeneric contents\n\n## Sub-Section\n\n- Some generic contents in list\n\n## Another sub-section\n\nSome generic stuff\nNot in list form\n\n### Another level in\n'

def test_markdown_section_from_text():
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
    result = MarkdownSection.from_text(input_text)
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

def test_markdown_from_text_nested():
    input_text = '''# 2025-01-01

Some example text for the day

## Work Done

- This is what I did today
- It was very neat
- I learned many things, fought many dragons

### Specific Nested Loop

These bits are nested on the 3rd loop'''
    result = MarkdownSection.from_text(input_text)
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
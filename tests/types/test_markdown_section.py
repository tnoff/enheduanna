from pytest import raises

from enheduanna.types.markdown_section import MarkdownSection, MarkdownException

def test_markdown_invalid_section():
    m = MarkdownSection('2025-02-16', 'generic contents')
    m.add_section(MarkdownSection('Sub-Section', '- Some generic contents in list', level=2))
    with raises(MarkdownException) as e:
        m.add_section(MarkdownSection('Sub-Section', '', level=2))
    assert 'Cannot add section, a section with title "Sub-Section" already exists' in str(e.value)

def test_markdown_section_remove():
    m = MarkdownSection('2025-02-16', 'generic contents')
    m.add_section(MarkdownSection('Sub-Section', '- Some generic contents in list', level=2))
    s = m.remove_section('Sub-Section')
    assert s.contents == '- Some generic contents in list'
    assert m.remove_section('foo') == None

def test_markdown_write():
    m = MarkdownSection('2025-02-16', 'generic contents')
    m.add_section(MarkdownSection('Sub-Section', '- Some generic contents in list', level=2))
    n = MarkdownSection('Another sub-section', 'Some generic stuff\nNot in list form', level=2)
    n.add_section(MarkdownSection('Another level in', '', level=3))
    m.add_section(n)
    result = m.write()
    assert result == '# 2025-02-16\n\ngeneric contents\n\n## Sub-Section\n\n- Some generic contents in list\n\n## Another sub-section\n\nSome generic stuff\nNot in list form\n\n### Another level in\n'

def test_markdown_generate_root():
    m = MarkdownSection('2025-02-16', 'generic contents')
    m.add_section(MarkdownSection('Sub-Section', '- Some generic contents in list', level=2))
    n = MarkdownSection('Another sub-section', 'Some generic stuff\nNot in list form', level=2)
    n.add_section(MarkdownSection('Another level in', '', level=3))
    m.add_section(n)
    result = m.sections[0].generate_root()
    assert result.title == 'Sub-Section'
    assert result.level == 1
    result = m.sections[1].generate_root()
    assert result.title == 'Another sub-section'
    assert result.level == 1
    assert result.sections[0].title == 'Another level in'

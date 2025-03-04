from pytest import raises

from enheduanna.types.markdown.markdown_section import MarkdownSection, MarkdownException
from enheduanna.types.markdown.rollup_section import RollupSection

def test_markdown_invalid_section():
    m = MarkdownSection('2025-02-16', 'generic contents')
    m.add_section(MarkdownSection('Sub-Section', '- Some generic contents in list', level=2))
    with raises(MarkdownException) as e:
        m.add_section(MarkdownSection('Sub-Section', '', level=2))
    assert 'Cannot add section, a section with title "Sub-Section" already exists' in str(e.value)

def test_markdown_invalid_level():
    m = MarkdownSection('2025-02-16', 'generic contents', level=2)
    with raises(MarkdownException) as e:
        m.add_section(MarkdownSection('Sub-Section', '', level=1))
    assert 'Cannot add section, has a lower level than this one' in str(e.value)

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

def test_markdown_section_merge():
    m = MarkdownSection('2025-02-16', 'generic contents')
    m1 = MarkdownSection('Work Done', '- Some example lines\n- That will be combined', level=2)
    m2 = MarkdownSection('Easy Work', '- Light work, was easy', level=3)
    m3 = MarkdownSection('Hard Work', '- Very hard, never do again', level=3)
    m1.add_section(m2)
    m1.add_section(m3)
    m.add_section(m1)

    n = MarkdownSection('2025-02-17', 'another generic contents')
    n1 = MarkdownSection('Work Done', '- More stuff done\n- even more!', level=2)
    n2 = MarkdownSection('Easy Work', '- Still very easy weee', level=3)
    n1.add_section(n2)
    n.add_section(n1)

    m.merge(n)
    assert m.contents == 'generic contents'
    assert m.title == '2025-02-16'
    assert m.sections[0].contents == '- Some example lines\n- That will be combined\n- More stuff done\n- even more!\n'
    assert m.sections[0].title == 'Work Done'
    assert m.sections[0].level == 2
    assert m.sections[0].sections[0].contents == '- Light work, was easy\n- Still very easy weee\n'
    assert m.sections[0].sections[0].title == 'Easy Work'
    assert m.sections[0].sections[0].level == 3
    assert m.sections[0].sections[1].contents == '- Very hard, never do again'
    assert m.sections[0].sections[1].title == 'Hard Work'
    assert m.sections[0].sections[1].level == 3

def test_markdown_section_group_contents():
    m = MarkdownSection('2025-02-16', 'generic contents')
    m1 = MarkdownSection('Work Done', '- Work on ticket (ABC-1234)\n- Work on another ticket (XYZ-234)\n- More work on the original ticket (ABC-1234)\nRandom input', level=2)
    m2 = MarkdownSection('Follow Ups', '- Generic follow ups', level=2)
    m.add_section(m1)
    m.add_section(m2)

    r = RollupSection('Work Done', regex='\\((?P<ticket>[A-Za-z]+-[0-9]+)\\)', groupBy='ticket')
    r2 = RollupSection('Follow Ups')
    m.group_contents(r)
    m.group_contents(r2)
    assert m.contents == 'generic contents'
    assert m.sections[0].contents == '- Work on ticket (ABC-1234)\n- More work on the original ticket (ABC-1234)\n\n- Work on another ticket (XYZ-234)\n\nRandom input'
    assert m.sections[1].contents == '- Generic follow ups'

def test_check_contents_empty():
    m = MarkdownSection('2025-02-16', 'generic contents')
    assert m.is_empty() == False
    m = MarkdownSection('2025-02-16', '- ')
    assert m.is_empty() == True
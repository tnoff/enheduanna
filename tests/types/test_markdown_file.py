from pathlib import Path
from tempfile import NamedTemporaryFile

from enheduanna.types.markdown_file import MarkdownFile

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
    with NamedTemporaryFile() as tmp:
        path = Path(tmp.name)
        path.write_text(input_text)
        mf = MarkdownFile.from_file(path)
        result = mf.root_section
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
    with NamedTemporaryFile() as tmp:
        path = Path(tmp.name)
        path.write_text(input_text)
        mf = MarkdownFile.from_file(path)
        result = mf.root_section
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

def test_read_and_write_same_file_after_removal():
    file_text = '''# 2025-02-20

## Testing Data

Heres some sections with example data
That has some stuff

## Remove Me

Remove this section later


    '''
    with NamedTemporaryFile() as tmp1:
        path1 = Path(tmp1.name)
        path1.write_text(file_text)
        mf = MarkdownFile.from_file(path1)
        mf.root_section.remove_section('Remove Me')
        mf.write()
        assert path1.read_text() == '# 2025-02-20\n\n## Testing Data\n\nHeres some sections with example data\nThat has some stuff\n'

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from enheduanna.types.config.media import MediaConfig
from enheduanna.types.markdown.markdown_file import MarkdownFile
from enheduanna.utils.media import (
    parse_media_filename,
    parse_collation_folder_name,
    organize_media_for_collation,
    update_markdown_media_references
)

def test_parse_media_filename_success():
    regex = r"Screenshot_(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_(?P<hour>\d{2})-(?P<minute>\d{2})-(?P<second>\d{2})"
    filename = "Screenshot_2025-01-20_14-30-45.png"
    result = parse_media_filename(filename, regex)
    assert result == datetime(2025, 1, 20, 14, 30, 45)

def test_parse_media_filename_no_match():
    regex = r"Screenshot_(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_(?P<hour>\d{2})-(?P<minute>\d{2})-(?P<second>\d{2})"
    filename = "random_file.png"
    result = parse_media_filename(filename, regex)
    assert result is None

def test_parse_media_filename_missing_groups():
    regex = r"Screenshot_(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    filename = "Screenshot_2025-01-20.png"
    result = parse_media_filename(filename, regex)
    assert result is None  # Missing hour, minute, second

def test_parse_collation_folder_name_success():
    folder_name = "2025-01-20_2025-01-26"
    date_format = "%Y-%m-%d"
    result = parse_collation_folder_name(folder_name, date_format)
    assert result is not None
    start, end = result
    assert start == datetime(2025, 1, 20, 0, 0, 0)
    assert end == datetime(2025, 1, 26, 23, 59, 59)

def test_parse_collation_folder_name_invalid():
    folder_name = "invalid_folder"
    date_format = "%Y-%m-%d"
    result = parse_collation_folder_name(folder_name, date_format)
    assert result is None

def test_organize_media_for_collation_move():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create source directory with test files
        source_dir = tmpdir / 'screenshots'
        source_dir.mkdir()

        # Create test media files
        file1 = source_dir / 'Screenshot_2025-01-20_14-30-45.png'
        file1.write_text('test image 1')
        file2 = source_dir / 'Screenshot_2025-01-21_09-15-30.png'
        file2.write_text('test image 2')
        file3 = source_dir / 'Screenshot_2025-01-30_10-00-00.png'  # Outside range
        file3.write_text('test image 3')

        # Create collation directory
        collation_dir = tmpdir / '2025-01-20_2025-01-26'
        collation_dir.mkdir()

        # Configure media
        config = MediaConfig(
            source_directory=source_dir,
            date_regex=r"Screenshot_(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_(?P<hour>\d{2})-(?P<minute>\d{2})-(?P<second>\d{2})",
            operation="move",
            extensions=[".png"],
            enabled=True
        )

        # Organize media
        start = datetime(2025, 1, 20, 0, 0, 0)
        end = datetime(2025, 1, 26, 23, 59, 59)
        mapping = organize_media_for_collation(collation_dir, start, end, config)

        # Check results
        assert len(mapping) == 2
        assert 'Screenshot_2025-01-20_14-30-45.png' in mapping
        assert 'Screenshot_2025-01-21_09-15-30.png' in mapping

        # Check files were moved
        assert not file1.exists()
        assert not file2.exists()
        assert file3.exists()  # Should not be moved (outside date range)

        # Check new files exist
        media_dir = collation_dir / 'media'
        assert media_dir.exists()
        assert (media_dir / '2025-01-20_14-30-45.png').exists()
        assert (media_dir / '2025-01-21_09-15-30.png').exists()

def test_organize_media_for_collation_copy():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create source directory with test files
        source_dir = tmpdir / 'screenshots'
        source_dir.mkdir()

        file1 = source_dir / 'Screenshot_2025-01-20_14-30-45.png'
        file1.write_text('test image 1')

        collation_dir = tmpdir / '2025-01-20_2025-01-26'
        collation_dir.mkdir()

        config = MediaConfig(
            source_directory=source_dir,
            date_regex=r"Screenshot_(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_(?P<hour>\d{2})-(?P<minute>\d{2})-(?P<second>\d{2})",
            operation="copy",
            extensions=[".png"],
            enabled=True
        )

        start = datetime(2025, 1, 20, 0, 0, 0)
        end = datetime(2025, 1, 26, 23, 59, 59)
        mapping = organize_media_for_collation(collation_dir, start, end, config)

        # Check file was copied (not moved)
        assert file1.exists()
        assert (collation_dir / 'media' / '2025-01-20_14-30-45.png').exists()

def test_organize_media_disabled():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source_dir = tmpdir / 'screenshots'
        source_dir.mkdir()

        file1 = source_dir / 'Screenshot_2025-01-20_14-30-45.png'
        file1.write_text('test image 1')

        collation_dir = tmpdir / '2025-01-20_2025-01-26'
        collation_dir.mkdir()

        config = MediaConfig(
            source_directory=source_dir,
            date_regex=r"Screenshot_(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_(?P<hour>\d{2})-(?P<minute>\d{2})-(?P<second>\d{2})",
            operation="move",
            extensions=[".png"],
            enabled=False
        )

        start = datetime(2025, 1, 20, 0, 0, 0)
        end = datetime(2025, 1, 26, 23, 59, 59)
        mapping = organize_media_for_collation(collation_dir, start, end, config)

        # Should not process anything when disabled
        assert len(mapping) == 0
        assert file1.exists()

def test_update_markdown_media_references():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create markdown file with image references
        md_file = tmpdir / 'test.md'
        md_file.write_text('''# Test Entry

## Work Done
- Fixed bug ![screenshot](~/Screenshots/Screenshot_2025-01-20_14-30-45.png)
- Another fix with HTML <img src="/home/user/Screenshots/Screenshot_2025-01-21_09-15-30.png">
''')

        # Create MarkdownFile object
        markdown_file = MarkdownFile.from_file(md_file)

        # Create mapping
        mapping = {
            'Screenshot_2025-01-20_14-30-45.png': '2025-01-20_14-30-45.png',
            'Screenshot_2025-01-21_09-15-30.png': '2025-01-21_09-15-30.png'
        }

        # Update references
        update_markdown_media_references([markdown_file], 'media', mapping)

        # Check updated content
        updated_content = md_file.read_text()
        assert './media/2025-01-20_14-30-45.png' in updated_content
        assert './media/2025-01-21_09-15-30.png' in updated_content
        assert '~/Screenshots/Screenshot_2025-01-20_14-30-45.png' not in updated_content
        assert '/home/user/Screenshots/Screenshot_2025-01-21_09-15-30.png' not in updated_content

def test_update_markdown_no_mapping():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        md_file = tmpdir / 'test.md'
        original_content = '# Test\nNo images here'
        md_file.write_text(original_content)

        markdown_file = MarkdownFile.from_file(md_file)

        # Empty mapping should not change file
        update_markdown_media_references([markdown_file], 'media', {})

        assert md_file.read_text() == original_content

def test_organize_media_custom_subfolder():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create source directory with test files
        source_dir = tmpdir / 'screenshots'
        source_dir.mkdir()

        file1 = source_dir / 'Screenshot_2025-01-20_14-30-45.png'
        file1.write_text('test image 1')

        collation_dir = tmpdir / '2025-01-20_2025-01-26'
        collation_dir.mkdir()

        # Configure media with custom subfolder
        config = MediaConfig(
            source_directory=source_dir,
            date_regex=r"Screenshot_(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_(?P<hour>\d{2})-(?P<minute>\d{2})-(?P<second>\d{2})",
            subfolder="images",
            operation="move",
            extensions=[".png"],
            enabled=True
        )

        start = datetime(2025, 1, 20, 0, 0, 0)
        end = datetime(2025, 1, 26, 23, 59, 59)
        mapping = organize_media_for_collation(collation_dir, start, end, config)

        # Check files were moved to custom subfolder
        images_dir = collation_dir / 'images'
        assert images_dir.exists()
        assert (images_dir / '2025-01-20_14-30-45.png').exists()

def test_update_markdown_custom_subfolder():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create markdown file with image references
        md_file = tmpdir / 'test.md'
        md_file.write_text('''# Test Entry

## Work Done
- Fixed bug ![screenshot](~/Screenshots/Screenshot_2025-01-20_14-30-45.png)
''')

        markdown_file = MarkdownFile.from_file(md_file)

        mapping = {
            'Screenshot_2025-01-20_14-30-45.png': '2025-01-20_14-30-45.png'
        }

        # Update references with custom subfolder
        update_markdown_media_references([markdown_file], 'images', mapping)

        # Check updated content uses custom subfolder
        updated_content = md_file.read_text()
        assert './images/2025-01-20_14-30-45.png' in updated_content
        assert './media/' not in updated_content

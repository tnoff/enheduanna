from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import time

from enheduanna.types.config.media import MediaConfig, MediaSource
from enheduanna.types.markdown.markdown_file import MarkdownFile
from enheduanna.utils.media import (
    parse_collation_folder_name,
    organize_media_for_collation,
    update_markdown_media_references
)

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

        # Create source folder with test files
        source_dir = tmpdir / 'screenshots'
        source_dir.mkdir()

        # Create test media files with specific mtimes
        file1 = source_dir / 'screenshot1.png'
        file1.write_text('test image 1')
        # Set mtime to 2025-01-20 14:30:45
        mtime1 = datetime(2025, 1, 20, 14, 30, 45).timestamp()
        os.utime(file1, (mtime1, mtime1))

        file2 = source_dir / 'screenshot2.png'
        file2.write_text('test image 2')
        # Set mtime to 2025-01-21 09:15:30
        mtime2 = datetime(2025, 1, 21, 9, 15, 30).timestamp()
        os.utime(file2, (mtime2, mtime2))

        file3 = source_dir / 'screenshot3.png'
        file3.write_text('test image 3')
        # Set mtime to 2025-01-30 10:00:00 (outside range)
        mtime3 = datetime(2025, 1, 30, 10, 0, 0).timestamp()
        os.utime(file3, (mtime3, mtime3))

        # Create collation directory
        collation_dir = tmpdir / '2025-01-20_2025-01-26'
        collation_dir.mkdir()

        # Configure media with new structure
        config = MediaConfig(
            sources=[
                MediaSource(
                    folder=source_dir,
                    operation="move",
                    subfolder="media"
                )
            ],
            extensions=[".png"],
            enabled=True
        )

        # Organize media
        start = datetime(2025, 1, 20, 0, 0, 0)
        end = datetime(2025, 1, 26, 23, 59, 59)
        mapping = organize_media_for_collation(collation_dir, start, end, config)

        # Check results
        assert len(mapping) == 2
        assert 'screenshot1.png' in mapping
        assert 'screenshot2.png' in mapping

        # Check files were moved
        assert not file1.exists()
        assert not file2.exists()
        assert file3.exists()  # Should not be moved (outside date range)

        # Check new files exist with correct naming
        media_dir = collation_dir / 'media'
        assert media_dir.exists()
        assert (media_dir / '2025-01-20_14-30-45.png').exists()
        assert (media_dir / '2025-01-21_09-15-30.png').exists()

        # Check mapping format
        assert mapping['screenshot1.png'] == ('media', '2025-01-20_14-30-45.png')
        assert mapping['screenshot2.png'] == ('media', '2025-01-21_09-15-30.png')

def test_organize_media_for_collation_copy():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create source folder with test files
        source_dir = tmpdir / 'screenshots'
        source_dir.mkdir()

        file1 = source_dir / 'screenshot1.png'
        file1.write_text('test image 1')
        mtime1 = datetime(2025, 1, 20, 14, 30, 45).timestamp()
        os.utime(file1, (mtime1, mtime1))

        collation_dir = tmpdir / '2025-01-20_2025-01-26'
        collation_dir.mkdir()

        config = MediaConfig(
            sources=[
                MediaSource(
                    folder=source_dir,
                    operation="copy",
                    subfolder="media"
                )
            ],
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

        file1 = source_dir / 'screenshot1.png'
        file1.write_text('test image 1')
        mtime1 = datetime(2025, 1, 20, 14, 30, 45).timestamp()
        os.utime(file1, (mtime1, mtime1))

        collation_dir = tmpdir / '2025-01-20_2025-01-26'
        collation_dir.mkdir()

        config = MediaConfig(
            sources=[
                MediaSource(
                    folder=source_dir,
                    operation="move",
                    subfolder="media"
                )
            ],
            extensions=[".png"],
            enabled=False
        )

        start = datetime(2025, 1, 20, 0, 0, 0)
        end = datetime(2025, 1, 26, 23, 59, 59)
        mapping = organize_media_for_collation(collation_dir, start, end, config)

        # Should not process anything when disabled
        assert len(mapping) == 0
        assert file1.exists()

def test_organize_media_multiple_sources():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create multiple source folders
        screenshots_dir = tmpdir / 'screenshots'
        screenshots_dir.mkdir()
        downloads_dir = tmpdir / 'downloads'
        downloads_dir.mkdir()

        # Create files in screenshots folder
        file1 = screenshots_dir / 'screenshot1.png'
        file1.write_text('screenshot')
        mtime1 = datetime(2025, 1, 20, 14, 30, 45).timestamp()
        os.utime(file1, (mtime1, mtime1))

        # Create files in downloads folder
        file2 = downloads_dir / 'download1.jpg'
        file2.write_text('download')
        mtime2 = datetime(2025, 1, 21, 9, 15, 30).timestamp()
        os.utime(file2, (mtime2, mtime2))

        collation_dir = tmpdir / '2025-01-20_2025-01-26'
        collation_dir.mkdir()

        # Configure multiple sources
        config = MediaConfig(
            sources=[
                MediaSource(
                    folder=screenshots_dir,
                    operation="move",
                    subfolder="media/screenshots"
                ),
                MediaSource(
                    folder=downloads_dir,
                    operation="copy",
                    subfolder="media/downloads"
                )
            ],
            extensions=[".png", ".jpg"],
            enabled=True
        )

        start = datetime(2025, 1, 20, 0, 0, 0)
        end = datetime(2025, 1, 26, 23, 59, 59)
        mapping = organize_media_for_collation(collation_dir, start, end, config)

        # Check both files were processed
        assert len(mapping) == 2
        assert 'screenshot1.png' in mapping
        assert 'download1.jpg' in mapping

        # Check files went to correct subfolders
        assert (collation_dir / 'media/screenshots' / '2025-01-20_14-30-45.png').exists()
        assert (collation_dir / 'media/downloads' / '2025-01-21_09-15-30.jpg').exists()

        # Check operations (move vs copy)
        assert not file1.exists()  # Moved
        assert file2.exists()  # Copied

        # Check mapping contains subfolder info
        assert mapping['screenshot1.png'] == ('media/screenshots', '2025-01-20_14-30-45.png')
        assert mapping['download1.jpg'] == ('media/downloads', '2025-01-21_09-15-30.jpg')

def test_organize_media_filename_conflict():
    """Test that filename conflicts are handled by appending counter"""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source_dir = tmpdir / 'screenshots'
        source_dir.mkdir()

        # Create two files with the same mtime
        file1 = source_dir / 'screenshot1.png'
        file1.write_text('test image 1')
        mtime = datetime(2025, 1, 20, 14, 30, 45).timestamp()
        os.utime(file1, (mtime, mtime))

        file2 = source_dir / 'screenshot2.png'
        file2.write_text('test image 2')
        os.utime(file2, (mtime, mtime))

        collation_dir = tmpdir / '2025-01-20_2025-01-26'
        collation_dir.mkdir()

        config = MediaConfig(
            sources=[
                MediaSource(
                    folder=source_dir,
                    operation="move",
                    subfolder="media"
                )
            ],
            extensions=[".png"],
            enabled=True
        )

        start = datetime(2025, 1, 20, 0, 0, 0)
        end = datetime(2025, 1, 26, 23, 59, 59)
        mapping = organize_media_for_collation(collation_dir, start, end, config)

        # Both files should be processed
        assert len(mapping) == 2

        # One should have base name, other should have counter
        media_dir = collation_dir / 'media'
        assert (media_dir / '2025-01-20_14-30-45.png').exists()
        assert (media_dir / '2025-01-20_14-30-45_1.png').exists()

def test_update_markdown_media_references():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create markdown file with image references
        md_file = tmpdir / 'test.md'
        md_file.write_text('''# Test Entry

## Work Done
- Fixed bug ![screenshot](~/Screenshots/screenshot1.png)
- Another fix with HTML <img src="/home/user/Downloads/download1.jpg">
''')

        # Create MarkdownFile object
        markdown_file = MarkdownFile.from_file(md_file)

        # Create mapping with new format (includes subfolder)
        mapping = {
            'screenshot1.png': ('media/screenshots', '2025-01-20_14-30-45.png'),
            'download1.jpg': ('media/downloads', '2025-01-21_09-15-30.jpg')
        }

        # Update references
        update_markdown_media_references([markdown_file], mapping)

        # Check updated content
        updated_content = md_file.read_text()
        assert './media/screenshots/2025-01-20_14-30-45.png' in updated_content
        assert './media/downloads/2025-01-21_09-15-30.jpg' in updated_content
        assert '~/Screenshots/screenshot1.png' not in updated_content
        assert '/home/user/Downloads/download1.jpg' not in updated_content

def test_update_markdown_no_mapping():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        md_file = tmpdir / 'test.md'
        original_content = '# Test\nNo images here'
        md_file.write_text(original_content)

        markdown_file = MarkdownFile.from_file(md_file)

        # Empty mapping should not change file
        update_markdown_media_references([markdown_file], {})

        assert md_file.read_text() == original_content

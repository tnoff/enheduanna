from pathlib import Path
from tempfile import TemporaryDirectory

from enheduanna.types.config.toc import TocConfig
from enheduanna.types.markdown.markdown_file import MarkdownFile
from enheduanna.types.markdown.markdown_section import MarkdownSection
from enheduanna.utils.toc import build_summary_toc_section, update_root_index


def _entry(file_dir: Path, name: str) -> MarkdownFile:
    '''
    Build a MarkdownFile stand-in for an entry with the given date name
    '''
    return MarkdownFile(file_dir / f'{name}.md', MarkdownSection(name, '', level=1))


def test_build_summary_toc_entries_and_media():
    with TemporaryDirectory() as tmpdir:
        file_dir = Path(tmpdir)
        media_dir = file_dir / 'media' / 'screenshots'
        media_dir.mkdir(parents=True)
        (media_dir / '2025-02-26_12-00-00.png').write_text('img')
        markdown_files = [_entry(file_dir, '2025-02-27'), _entry(file_dir, '2025-02-28')]
        section = build_summary_toc_section(file_dir, markdown_files, ['.png'], TocConfig())
        assert section.title == 'Contents'
        assert section.write() == (
            '## Contents\n\n'
            '### Entries\n\n'
            '- [2025-02-27](./2025-02-27.md)\n'
            '- [2025-02-28](./2025-02-28.md)\n\n'
            '### Media\n\n'
            '- [2025-02-26_12-00-00.png](./media/screenshots/2025-02-26_12-00-00.png)\n'
        )


def test_build_summary_toc_entries_only():
    with TemporaryDirectory() as tmpdir:
        file_dir = Path(tmpdir)
        section = build_summary_toc_section(file_dir, [_entry(file_dir, '2025-02-27')],
                                            ['.png'], TocConfig(include_media=False))
        assert [s.title for s in section.sections] == ['Entries']


def test_build_summary_toc_media_only():
    with TemporaryDirectory() as tmpdir:
        file_dir = Path(tmpdir)
        (file_dir / 'shot.PNG').write_text('img')
        section = build_summary_toc_section(file_dir, [], ['.png'], TocConfig(include_entries=False))
        assert [s.title for s in section.sections] == ['Media']
        assert section.sections[0].contents == '- [shot.PNG](./shot.PNG)'


def test_build_summary_toc_empty_returns_none():
    with TemporaryDirectory() as tmpdir:
        file_dir = Path(tmpdir)
        assert build_summary_toc_section(file_dir, [], ['.png'], TocConfig()) is None


def test_update_root_index_success():
    with TemporaryDirectory() as tmpdir:
        entries = Path(tmpdir)
        for name in ['2025-01-20_2025-01-26', '2025-02-24_2025-03-02']:
            folder = entries / name
            folder.mkdir()
            (folder / 'summary.md').write_text('# summary')
        # Folder without a summary is skipped
        (entries / 'scratch').mkdir()
        path = update_root_index(entries, 'summary.md', TocConfig())
        assert path == entries / 'index.md'
        assert path.read_text() == (
            '# Notes Index\n\n'
            '- [2025-02-24 -> 2025-03-02](./2025-02-24_2025-03-02/summary.md)\n'
            '- [2025-01-20 -> 2025-01-26](./2025-01-20_2025-01-26/summary.md)\n'
        )


def test_update_root_index_no_summaries_returns_none():
    with TemporaryDirectory() as tmpdir:
        entries = Path(tmpdir)
        (entries / 'scratch').mkdir()
        assert update_root_index(entries, 'summary.md', TocConfig()) is None

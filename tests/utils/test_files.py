from pathlib import Path
from tempfile import TemporaryDirectory

from enheduanna.utils.files import normalize_file_name, list_markdown_files, find_last_markdown_file

def test_list_files():
    with TemporaryDirectory(prefix='a') as tmpdir:
        weekly_dir = Path(tmpdir) / '2025-02-10_2025-02-16'
        weekly_dir.mkdir()
        tmp1 = weekly_dir / '2025-02-11.md'
        tmp1.touch()
        tmp2 = weekly_dir / '2025-02-12.md'
        tmp2.touch()
        tmp3 = weekly_dir / 'summary.md'
        tmp3.touch()
        files = list_markdown_files(Path(tmpdir))
        assert files[0] == Path(tmp1)
        assert files[1] == Path(tmp2)
        file = find_last_markdown_file(Path(tmpdir))
        assert file == tmp2

        # Test with include non days
        files = list_markdown_files(Path(tmpdir), only_include_entry=False)
        assert len(files) == 3
        file = find_last_markdown_file(Path(tmpdir), only_include_entry=False)
        assert file == tmp3

def test_normalize_filename():
    assert normalize_file_name('foo') == 'foo'
    assert normalize_file_name('temp.foo') == 'temp.foo'
    assert normalize_file_name('go giants!') == 'go giants_'

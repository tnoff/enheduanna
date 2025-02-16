from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from enheduanna.utils.files import list_markdown_files

def test_list_files():
    with TemporaryDirectory(prefix='a') as tmpdir:
        with NamedTemporaryFile(suffix='.md', dir=tmpdir, prefix='a') as tmp1:
            with NamedTemporaryFile(suffix='.md', dir=tmpdir, prefix='b') as tmp2:
                files = list_markdown_files(Path(tmpdir))
                assert files[0] == Path(tmp1.name)
                assert files[1] == Path(tmp2.name)
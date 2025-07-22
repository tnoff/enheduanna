from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from freezegun import freeze_time

from enheduanna.types.config import Config
from enheduanna.types.config.file import FileConfig
from enheduanna.types.config.collation import CollationConfig, CollationType
from enheduanna.utils.collation import create_parent_folder

@freeze_time('2025-03-01 12:00:00', tz_offset=0)
def test_create_parent_folder():
    with TemporaryDirectory() as tmpdir:
        config = Config(FileConfig(note_directory=tmpdir), CollationConfig())
        result = create_parent_folder(config, date(2025, 3, 1))
        assert str(result) == str(Path(tmpdir) / '2025-02-24_2025-03-02')

        config = Config(FileConfig(note_directory=tmpdir), CollationConfig(type=CollationType.MONTHLY))
        result = create_parent_folder(config, date(2025, 3, 1))
        assert str(result) == str(Path(tmpdir) / '2025-03-01_2025-03-31')

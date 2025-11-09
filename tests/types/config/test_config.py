from pathlib import Path
from tempfile import NamedTemporaryFile

from enheduanna.types.config.collation import CollationType
from enheduanna.types.config import Config

def test_load_yaml_basic_file():
    test_data = '''---
file:
  entries_directory: /home/user/foo
'''
    with NamedTemporaryFile() as tmp:
        path = Path(tmp.name)
        path.write_text(test_data)
        c = Config.from_yaml(path)
        assert c.file.entries_directory == Path('/home/user/foo')

def test_load_yaml_entry_sections():
    test_data = '''---
file:
  entry_sections:
    - title: Work Done
      contents: foo bar
      level: 2
      rollover: true
'''
    with NamedTemporaryFile() as tmp:
        path = Path(tmp.name)
        path.write_text(test_data)
        c = Config.from_yaml(path)
        assert c.file.entry_sections[0].title == 'Work Done'
        assert c.file.entry_sections[0].contents == 'foo bar'

def test_collation_type():
    test_data = '''---
'''
    with NamedTemporaryFile() as tmp:
        path = Path(tmp.name)
        path.write_text(test_data)
        c = Config.from_yaml(path)
        assert c.collation.type == CollationType.WEEKLY

def test_collation_type():
    test_data = '''---
collation:
  type: monthly
'''
    with NamedTemporaryFile() as tmp:
        path = Path(tmp.name)
        path.write_text(test_data)
        c = Config.from_yaml(path)
        assert c.collation.type == CollationType.MONTHLY

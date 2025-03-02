from pathlib import Path
from tempfile import NamedTemporaryFile

from enheduanna.types.config.config import Config

def test_load_yaml_basic_file():
    test_data = '''---
file:
  note_directory: /home/user/foo
'''
    with NamedTemporaryFile() as tmp:
        path = Path(tmp.name)
        path.write_text(test_data)
        c = Config.from_yaml(path)
        assert c.file.note_directory == Path('/home/user/foo')

def test_load_yaml_daily_sections():
    test_data = '''---
file:
  daily_sections:
    - title: Work Done
      contents: foo bar
      level: 2
      carryover: true
'''
    with NamedTemporaryFile() as tmp:
        path = Path(tmp.name)
        path.write_text(test_data)
        c = Config.from_yaml(path)
        assert c.file.daily_sections[0].title == 'Work Done'
        assert c.file.daily_sections[0].contents == 'foo bar'
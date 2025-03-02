from json import loads

from pathlib import Path
from pydantic.dataclasses import dataclass
from pyaml_env import parse_config

from enheduanna.types.config.file import FileConfig

@dataclass
class Config:
    '''
    Config options
    '''
    file: FileConfig

def from_yaml(file_path: Path) -> Config:
    '''
    Load config from a yaml file
    '''
    config = {}
    if file_path.exists():
        config = parse_config(file_path)
        if isinstance(config, str):
            config = loads(config)

    file_config_opts = config.get('file', {})
    file_config = FileConfig(**file_config_opts)

    final_config = Config(file_config)
    return final_config

Config.from_yaml = from_yaml

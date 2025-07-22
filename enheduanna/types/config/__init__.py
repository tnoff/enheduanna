from json import loads

from pathlib import Path
from pydantic.dataclasses import dataclass
from pyaml_env import parse_config

from enheduanna.types.config.collation import CollationConfig
from enheduanna.types.config.file import FileConfig

@dataclass
class Config:
    '''
    Config options
    '''
    file: FileConfig
    collation: CollationConfig

def from_yaml(file_path: Path) -> Config:
    '''
    Load config from a yaml file
    '''
    config = {}
    if file_path.exists():
        config = parse_config(file_path)
        if isinstance(config, str):
            config = loads(config)

    try:
        file_config_opts = config.get('file', {})
    except AttributeError:
        file_config_opts = {}
    file_config = FileConfig(**file_config_opts)

    try:
        collation_config_opts = config.get('collation', {})
    except AttributeError:
        collation_config_opts = {}
    collation_config = CollationConfig(**collation_config_opts)

    final_config = Config(file=file_config, collation=collation_config)
    return final_config

Config.from_yaml = from_yaml

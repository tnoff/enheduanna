from pydantic.dataclasses import dataclass

from enheduanna.types.config.jira import CliJiraConfig
from enheduanna.types.config.file import CliFileConfig

@dataclass
class CliConfig:
    jira_config: CliJiraConfig
    file_config: CliFileConfig

def from_json(json_data: dict) -> CliConfig:
    '''
    Load config from json
    '''
    file_config = json_data.get('file', {})
    jira_config = json_data.get('jira', {}).get('config', {})

    return CliConfig(CliJiraConfig(**jira_config), CliFileConfig(**file_config))

CliConfig.from_json = from_json
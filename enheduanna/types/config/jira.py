from jira import JIRA
from jira.exceptions import JIRAError
from pydantic.dataclasses import dataclass

@dataclass
class CliJiraConfig:
    '''
    Cli config for jira options
    '''
    server_url: str = None
    user_email: str = None
    user_token: str = None

    def __post_init__(self):
        self._client = None
        if self.server_url and self.user_email and self.user_token:
            try:
                self._client = JIRA(server=self.server_url,
                                    basic_auth=(self.user_email, self.user_token))
                self._client.current_user()
            except JIRAError as e:
                raise AssertionError(f'Unable to validate JIRA connection') from e
    
    @property
    def client(self) -> JIRA:
        return self._client
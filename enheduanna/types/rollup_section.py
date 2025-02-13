from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass

@dataclass
class RollupSection:
    '''
    RollupSections for Markdown
    '''
    title: str
    regex: str = None
    groupBy: str = None

    def __str__(self):
        return self.title

RollupSection.from_json = TypeAdapter(RollupSection).validate_json

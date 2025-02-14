from typing import Self

from pydantic import TypeAdapter, model_validator
from pydantic.dataclasses import dataclass

@dataclass
class RollupSection:
    '''
    RollupSections for Markdown
    '''
    title: str
    regex: str = None
    groupBy: str = None

    @model_validator(mode='after')
    def validate_groupBy(self) -> Self:
        '''
        Check regex and groupBy fields are valid
        '''
        if self.regex and not self.groupBy:
            raise AssertionError('Regex requires groupBy be set')
        if self.groupBy and not self.regex:
            raise AssertionError('GroupBy requires regex be set')
        if self.regex and self.groupBy:
            if f'(?P<{self.groupBy}' not in self.regex:
                raise AssertionError('GroupBy field must be gathered in regex')
        return self

    def __str__(self):
        return self.title

RollupSection.from_json = TypeAdapter(RollupSection).validate_json

from typing import Self

from pydantic import model_validator
from pydantic.dataclasses import dataclass

from enheduanna.types.conditions.base_condition_type import BaseConditionType
from enheduanna.types.conditions.day_of_week import TYPE_NAME as day_of_week_type_name

VALID_TYPES = [
    day_of_week_type_name,
]

@dataclass
class Condition:
    '''
    Day of Week Conditions
    '''
    title: str
    type: str
    condition: BaseConditionType

    @model_validator(mode='after')
    def validate_type(self) -> Self:
        '''
        Validate type
        '''
        if self.type not in VALID_TYPES:
            raise AssertionError(f'Invalid type given {self.type}')
        return self

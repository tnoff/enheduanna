from typing import Self

from pydantic import model_validator
from pydantic.dataclasses import dataclass

from enheduanna.types.conditions.base_condition_type import BaseConditionType

TYPE_NAME = 'day_of_week'

@dataclass
class DayOfWeek(BaseConditionType):
    '''
    Day of Week Conditions
    '''
    value: int

    @model_validator(mode='after')
    def validate_value(self) -> Self:
        '''
        Validate value
        '''
        if self.value < 0:
            raise AssertionError(f'Invalid value {self.value}, must be non-negative')
        if self.value > 6:
            raise AssertionError(f'Invalid value {self.value}, must be less than 7')
        return self

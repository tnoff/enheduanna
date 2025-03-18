from pathlib import Path
from typing import Self, List

from pydantic import Field
from pydantic import model_validator
from pydantic.dataclasses import dataclass

from enheduanna.types.conditions.condition import Condition

@dataclass
class ConditionsConfig:
    '''
    Conditions options
    '''
    conditions:  List[Condition] = Field(default_factory=list)
from enum import Enum
from pydantic.dataclasses import dataclass


class CollationType(Enum):
    '''
    Accepted collation types
    '''
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'

@dataclass
class CollationConfig:
    '''
    Collation Settings
    '''
    type: CollationType = CollationType.WEEKLY

from pydantic import ValidationError
from pytest import raises


from enheduanna.types.conditions.condition import Condition
from enheduanna.types.conditions.day_of_week import DayOfWeek

def test_invalid_condition_name():
    day_of_week = DayOfWeek(1)
    with raises(ValidationError) as error:
        Condition('on_monday', 'foo', day_of_week)
    assert 'Invalid type given' in str(error.value)

def test_day_of_week_condition():
    day_of_week = DayOfWeek(1)
    condition = Condition('on_monday', 'day_of_week', day_of_week)
    assert condition.title == 'on_monday'

def test_day_of_week_invalid():
    with raises(ValidationError) as error:
        DayOfWeek(-1)
    assert 'Invalid value -1, must be non-negative' in str(error.value)
    with raises(ValidationError) as error:
        DayOfWeek(7)
    assert 'Invalid value 7, must be less than 7' in str(error.value)

from datetime import date

from enheduanna.utils.days import get_end_of_week, get_start_of_week

def test_date_functions():
    day = date(2025, 2, 15)
    assert get_end_of_week(day) == date(2025, 2, 16)
    assert get_start_of_week(day) == date(2025, 2, 10)
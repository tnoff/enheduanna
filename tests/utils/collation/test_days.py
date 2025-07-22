from datetime import date

from enheduanna.utils.collation.days import get_end_of_week, get_start_of_week
from enheduanna.utils.collation.days import get_start_of_month, get_end_of_month

def test_date_functions():
    day = date(2025, 2, 15)
    assert get_end_of_week(day) == date(2025, 2, 16)
    assert get_start_of_week(day) == date(2025, 2, 10)

def test_month_functions():
    assert get_start_of_month(date(2025, 1, 1)) == date(2025, 1, 1)
    assert get_start_of_month(date(2025, 7, 15)) == date(2025, 7, 1)
    assert get_end_of_month(date(2025, 12, 12)) == date(2025, 12, 31)
    assert get_end_of_month(date(2025, 3, 1)) == date(2025, 3, 31)
from datetime import date, timedelta

def get_start_of_week(day: date) -> date:
    '''
    Get start of week
    '''

    while True:
        if day.weekday() == 0:
            return day
        day = day - timedelta(days=1)

def get_end_of_week(day: date) -> date:
    '''
    Get end of week
    '''
    while True:
        if day.weekday() == 6:
            return day
        day = day + timedelta(days=1)


def get_start_of_month(day: date) -> date:
    '''
    Get start of month
    '''
    # Already first day
    return date(day.year, day.month, 1)

def get_end_of_month(day: date) -> date:
    '''
    Get end of month
    '''
    # If december, return hardcode
    if day.month == 12:
        return date(day.year, 12, 31)
    # Else add month and subtract one
    return date(day.year, day.month + 1, 1) - timedelta(days=1)

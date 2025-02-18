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

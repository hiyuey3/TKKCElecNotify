import re
from datetime import datetime, timedelta
from icalendar import Calendar

# 当前 session
loginSession = None
latest_login_req_cookie = None

def date_mapper(lesson_rank: str) -> tuple:
    """ 课时映射函数 """
    START_TIME_MAPPER = {
        '1': '08:00', '2': '08:55', '3': '10:00', '4': '10:45',
        '午1': '12:30', '午2': '13:25', '5': '14:30', '6': '15:25',
        '7': '16:30', '8': '17:25', '9': '19:30', '10': '20:25', '11': '21:20'
    }
    END_TIME_MAPPER = {
        '1': '08:45', '2': '09:40', '3': '10:45', '4': '11:40',
        '午1': '13:15', '午2': '14:10', '5': '15:15', '6': '16:10',
        '7': '17:15', '8': '18:10', '9': '20:15', '10': '21:10', '11': '22:05'
    }
    start_and_end_rank = lesson_rank.split('-')
    return (START_TIME_MAPPER.get(start_and_end_rank[0], '08:00'),
            END_TIME_MAPPER.get(start_and_end_rank[1], '08:45'))
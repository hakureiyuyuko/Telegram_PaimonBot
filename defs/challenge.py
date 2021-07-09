from pyrogram.types import Message
from datetime import datetime


def get_day(message: Message):
    mes = message.text
    if '一' in mes:
        day = 1
    elif '二' in mes:
        day = 2
    elif '三' in mes:
        day = 3
    elif '四' in mes:
        day = 4
    elif '五' in mes:
        day = 5
    elif '六' in mes:
        day = 6
    else:
        day = datetime.now().isoweekday()
        if '明' in mes:
            if day == 7:
                day = 1
            else:
                day += 1
    return day

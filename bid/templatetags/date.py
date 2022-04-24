from django import template
import os
register = template.Library()
import datetime
from pytz import timezone

@register.filter(name = 'dateParse')
def dateParse(value, arg):
    """Removes all values of arg from the given string"""
    today_date = datetime.datetime.now(timezone('Asia/Kolkata'))
    date = value.astimezone(timezone('Asia/Kolkata'))
    if arg == 'date':
        return f"{date.day} {date.strftime('%B')} {date.hour - 12}:30"
    else:
        return f"{date.hour - 12}:{date.minute} PM"


@register.filter(name = 'dateCheck')
def dateCheck(date):
    game_date = date.astimezone(timezone('Asia/Kolkata'))
    today_date = datetime.datetime.now(timezone('Asia/Kolkata')) + datetime.timedelta(minutes=1)
    print(today_date < game_date and (game_date - today_date).days <=1, today_date, game_date)
    return today_date < game_date and (game_date - today_date).days <=1


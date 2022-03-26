from django import template
import os
register = template.Library()
import datetime
from pytz import timezone

@register.filter(name = 'dateParse')
def dateParse(value, arg):
    """Removes all values of arg from the given string"""
    today_date = datetime.datetime.now(timezone('Asia/Kolkata'))
    if arg == 'date':
        return f"{value.day} {value.strftime('%B')} {value.hour - 12}:30"
    else:
        return f"{value.hour - 12}:{value.minute} PM"


@register.filter(name = 'dateCheck')
def dateCheck(date):
    today_date = datetime.datetime.now(timezone('Asia/Kolkata')) + datetime.timedelta(minutes=5)
    return today_date < date and (date - today_date).days <=1


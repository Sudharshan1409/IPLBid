from pytz import timezone
from iplBid.settings import DREAM11_PLAYERS_USERNAMES as usernames
import datetime
from django import template
from django.contrib.auth.models import User
import os
from iplBid.settings import CURRENT_YEAR

register = template.Library()


@register.filter(name='dateParse')
def dateParse(value, arg):
    """Removes all values of arg from the given string"""
    date = value.astimezone(timezone('Asia/Kolkata'))
    if arg == 'date':
        return f"{date.day} {date.strftime('%B')} {date.hour - 12}:30"
    else:
        return f"{date.hour - 12}:{date.minute} PM"


@register.filter(name='dateCheck')
def dateCheck(date):
    game_date = date.astimezone(timezone('Asia/Kolkata'))
    today_date = datetime.datetime.now(timezone('Asia/Kolkata'))
    print(today_date < game_date and (game_date - today_date).days <= 1, today_date, game_date)
    return today_date < game_date and (game_date - today_date).days <= 1


@register.filter(name='usernameCheck')
def usernameCheck(username):
    return username in usernames


@register.filter(name='nameCheck')
def nameCheck(name):
    if not name:
        return None
    if '&' in name:
        name_split = name.split('&')
        return name_split[0] + ' & ' + name_split[1]
    return name


@register.filter(name='checkPlayOffsCondition')
def checkPlayOffsCondition(game, user):
    game_date = game.date.astimezone(timezone('Asia/Kolkata'))
    today_date = datetime.datetime.now(timezone('Asia/Kolkata'))
    if today_date > game_date or (not game.isPlayOffs or user.is_superuser):
        return True
    return False


@register.filter(name='convertToJson')
def convertToJson(value):
    import json

    from django.utils.safestring import mark_safe
    _js_escapes = {
        ord('\\'): '\\u005C',
        ord('\''): '\\u0027',
        ord('"'): '\\u0022',
        ord('>'): '\\u003E',
        ord('<'): '\\u003C',
        ord('&'): '\\u0026',
        ord('='): '\\u003D',
        ord('-'): '\\u002D',
        ord(';'): '\\u003B',
        ord('`'): '\\u0060',
        ord('\u2028'): '\\u2028',
        ord('\u2029'): '\\u2029'
    }
    return mark_safe(str(json.dumps(value)).translate(_js_escapes))


@register.filter(name='checkRemainderCondition')
def checkRemainderCondition(userId, requestPath):
    if not userId:
        return False
    user = User.objects.get(id=userId)
    active_year = user.active_year.year
    if active_year != int(CURRENT_YEAR):
        return False
    if requestPath == '/':
        return True
    if '/bid/user' not in requestPath:
        return False
    profile = user.profiles.filter(year=active_year).first()
    pathProfileId = int(requestPath.split('/user/')[1].split('/')[0])
    if pathProfileId == profile.id:
        return True
    return False


@register.filter(name='remainderCheck')
def remainderCheck(userId):
    user = User.objects.get(id=userId)
    active_year = user.active_year.year
    profile = user.profiles.filter(year=active_year).first()
    if profile.remainder:
        return True
    return False

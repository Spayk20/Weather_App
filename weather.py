import os
import requests
import geocoder
import datetime


API_KEY = os.environ.get('API_KEY')
HOST = 'https://api.openweathermap.org/data/2.5/'
DAYS = [
    {"num": 0, "title": "Понеділок", "active": False, "color": "#FFE739", "order": [0,1,2,3,4,5,6], "temp": 0, "type": "-"},
    {"num": 1, "title": "Вівторок",  "active": False, "color": "#FFE739", "order": [1,2,3,4,5,6,0], "temp": 0, "type": "-"},
    {"num": 2, "title": "Середа",    "active": False, "color": "#FFE739", "order": [2,3,4,5,6,0,1], "temp": 0, "type": "-"},
    {"num": 3, "title": "Четвер",    "active": False, "color": "#FFE739", "order": [3,4,5,6,0,1,2], "temp": 0, "type": "-"},
    {"num": 4, "title": "П'ятниця",  "active": False, "color": "#FFE739", "order": [4,5,6,0,1,2,3], "temp": 0, "type": "-"},
    {"num": 5, "title": "Субота",    "active": False, "color": "#36FF72", "order": [5,6,0,1,2,3,4], "temp": 0, "type": "-"},
    {"num": 6, "title": "Неділя",    "active": False, "color": "#36FF72", "order": [6,0,1,2,3,4,5], "temp": 0, "type": "-"}
]


def today():
    g = geocoder.ip('me')
    city = g.city
    lat = g.lat
    lon = g.lng


    req = requests.get(f'{HOST}weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ua').json()
    res = {
        "city"     : req['name'],
        "dis"      : req['weather'][0]['description'],
        "weat_type": req['weather'][0]['id'],
        "icon"     : req['weather'][0]['icon'],
        "temp"     : int(round(req['main']['temp'])),
        "feels"    : str(round(req['main']['feels_like'])) + "°C",
        "humidity" : str(round(req['main']['humidity'] / 1000 * 750, 2)),
        "wind"     : req['wind'],
        }
    return res


def week():
    today = datetime.datetime.today()
    DAYS[today.weekday()]['active'] = True

    for i in DAYS:
        if DAYS[today.weekday()]['active']:
            order = DAYS[today.weekday()]['order']
    g = geocoder.ip('me')
    lat = g.lat
    lon = g.lng

    req = requests.get(f'{HOST}onecall?/exclude=daily&lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ua').json()
    res = [DAYS[i] for i in order]

    for i in req['daily']:
        index = req['daily'].index(i)
        if index == 7:
            break
        res[index]['temp'] = round(i['temp']['day'])
        res[index]['type'] = i['weather'][0]['description']
        res[index]['icon'] = i['weather'][0]['icon']
    return res

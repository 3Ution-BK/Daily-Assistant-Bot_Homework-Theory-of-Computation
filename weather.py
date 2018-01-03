""" Basic weather module

    This module implement the weather program.
"""

import urllib.request
import json

# Important token
APPID = '&APPID=' + 'YOUR_API_KEY'

# Constant
WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q='
UNIT = '&units=Metric'
POWERED_BY = 'powered by OpenWeatherMap'


def get_weather(city):
    """ Get the weather of the city

    It will check the weather in OpenWeatherMap, and return result.

    Args:
        city: the city.

    Returns:
        string that contain the result
    Raises:
        None.
    """
    try:
        with urllib.request.urlopen(WEATHER_URL + city + UNIT + APPID) as url:
            weather_data = json.loads(url.read().decode())

            # Get the weather info
            weather = str(weather_data.get('weather')[0].get('description'))

            temp = str(int(weather_data.get('main').get('temp')))
            humidity = str(int(weather_data.get('main').get('humidity')))

            wind_deg = str(weather_data.get('wind').get('deg'))
            wind_speed = str(weather_data.get('wind').get('speed'))

            # Return the result
            return ('Weather in ' + city.capitalize() + ':\n' +
                    weather.capitalize() + '\n' +
                    temp + '°C' + '\n' +
                    'Wind: ' + wind_speed + 'm/s, ' + wind_deg + '°' + '\n' +
                    'Humidity: ' + humidity + '%\n' +
                    POWERED_BY)

    except urllib.error.HTTPError:
        # City no found
        return 'Sorry. I cannot found ' + city + '.'

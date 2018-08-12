from requests import get
from time import sleep
API_KEY = "949a7ca4395f4f1b9b6220440171902"
ZIP = "50014"


def getData():
    """This returns a json object with the current weather data"""
    # attempts request 10 times, avoids exception we had with darksky and gets a response. Added here just in case.
    for attempt in range(10):
        try:
            # make a request to the url and return it in json format
            url = "http://api.apixu.com/v1/current.json?key=%s&q=%s" % (API_KEY, ZIP)
            return get(url).json()
        except:
            # Wait .05 seconds and try again
            sleep(.05)
            pass


def getTemperature(metric=False):
    """This returns the temperature from the weather data"""
    # checks if user wants metric or USCS
    if metric:
        # retrieves data
        data = getData()["current"]["temp_c"]
        # checks if data exists
        if data:
            # returns temperature in celcius
            return data
        else:
            # returns NA
            return "NA"
    else:
        # retrieves data
        data = getData()["current"]["temp_f"]
        # checks if data exists
        if data:
            # returns temperature in fahrenheit
            return data
        else:
            # returns NA
            return "NA"


def getPressure(metric=False):
    """This returns the pressure from the weather data"""
    # checks if user wants metric or USCS
    if metric:
        # retrieves data
        data = getData()["current"]["pressure_mb"]
        # checks if data exists
        if data:
            # returns barometric pressure in millibars
            return data
        else:
            # returns NA
            return "NA"
    else:
        # retrieves data
        data = getData()["current"]["pressure_in"]
        # checks if data exists
        if data:
            # returns barometric pressure in inHg
            return data
        else:
            # returns NA
            return "NA"


def getWindSpeed(metric=False):
    """This returns the wind speed from the weather data"""
    # checks if user wants metric or USCS
    if metric:
        # retrieves data
        data = getData()["current"]["wind_kph"]
        # checks if data exists
        if data:
            # returns wind speed in kph
            return data
        else:
            # returns NA
            return "NA"
    else:
        # retrieves data
        data = getData()["current"]["wind_mph"]
        # checks if data exists
        if data:
            # returns wind speed in mph
            return data
        else:
            # returns NA
            return "NA"


def getWindDirection():
    """This returns the wind direction from the weather data"""
    # retrieves data
    data = getData()["current"]["wind_dir"]
    # checks if data exists
    if data:
        # returns wind direction
        return data
    else:
        # returns NA
        return "NA"

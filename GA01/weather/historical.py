from requests import get
from time import time, sleep
API_KEY = "insert_Here"
LAT = "42.0308"
LNG = "-93.6319"
currentTime = round(time())


def getData(tme=currentTime):
    """This returns a json object with the current weather data"""
    # attempts request 10 times
    for attempt in range(10):
        try:
            # make a request to the url and return it in json format
            url = "https://api.darksky.net/forecast/%s/%s,%s,%s?exclude=minutely,hourly,daily,alerts,flags" % (API_KEY, LAT, LNG, tme)
            return get(url).json()
        except:
            # Wait .05 seconds and try again
            sleep(.05)
            pass


def convertTemp(t, convertTo="C"):
    """convert temperature to Celsius and round to tenths place
       always has fahrenheit temperatures from source
    """
    # check if target temperature is celcius (metric)
    if convertTo == "C":
        # returns celcius (metric) temperature
        return round(((5 / 9) * (t - 32)), 1)
    else:
        # returns fahrenheit but rounded
        return round(t, 1)


def convertWindSpeed(ws, convertTo="KMH"):
    """return wind speed"""
    # check if target wind speed is kilometers per hour (metric)
    if convertTo == "KMH":
        # returns kilometers per hour (metrix)
        return round(ws * 1.61, 1)
    else:
        # returns miles per hour but rounded
        return round(ws, 1)


def convertPressure(p, convertTo="inHg"):
    """returns pressure"""
    # check if target wind speed is kilometers per hour (metric)
    if convertTo == "inHg":
        # returns inches of mercury but rounded
        return round(p * 0.02953, 1)
    else:
        # returns millibars
        return round(p, 1)


def convertToWindDirection(wb):
    """returns wind direction by converting to cardinal direction"""
    if wb >= 0 and wb < 11.25:
        return "N"
    elif wb >= 11.25 and wb < 33.75:
        return "NNE"
    elif wb >= 33.75 and wb < 56.25:
        return "NE"
    elif wb >= 56.25 and wb < 78.75:
        return "ENE"
    elif wb >= 78.75 and wb < 101.25:
        return "E"
    elif wb >= 101.25 and wb < 123.75:
        return "ESE"
    elif wb >= 123.75 and wb < 146.25:
        return "SE"
    elif wb >= 146.25 and wb < 168.75:
        return "SSE"
    elif wb >= 168.75 and wb < 191.25:
        return "S"
    elif wb >= 191.25 and wb < 213.75:
        return "SSW"
    elif wb >= 213.75 and wb < 236.25:
        return "SW"
    elif wb >= 236.25 and wb < 258.75:
        return "WSW"
    elif wb >= 258.75 and wb < 281.25:
        return "W"
    elif wb >= 281.25 and wb < 303.75:
        return "WNW"
    elif wb >= 303.75 and wb < 326.25:
        return "NW"
    elif wb >= 326.25 and wb < 348.75:
        return "NNW"
    elif wb >= 348.75 and wb < 360:
        return "N"
    else:
        return "NA"


def getTemperature(tempScale="F", tme=currentTime):
    """returns temperature"""
    # retrieves data
    data = getData(tme)
    # checks if data exists
    if data:
        # returns temperature in tempScale
        return convertTemp(data["currently"]["temperature"], tempScale)
    else:
        # returns NA
        return "NA"


def getWindSpeed(wsScale="MPH", tme=currentTime):
    """returns wind speed"""
    # retrieves data
    data = getData(tme)
    # checks if data exists
    if data:
        # returns wind speed in wsScale
        return convertWindSpeed(data["currently"]["windSpeed"], wsScale)
    else:
        # returns NA
        return "NA"


def getPressure(prScale="inHg", tme=currentTime):
    """return pressure"""
    # retrieves data
    data = getData(tme)
    # checks if data exists
    if data:
        # returns pressure in prScale
        return convertPressure(data["currently"]["pressure"], prScale)
    else:
        # returns NA
        return "NA"


def getWindDirection(tme=currentTime):
    """return wind direction"""
    # retrieves data
    data = getData(tme)
    # checks if data exists
    if data:
        # returns wind direction
        return convertToWindDirection(data["currently"]["windBearing"])
    else:
        # returns NA
        return "NA"

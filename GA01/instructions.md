# User Manual

## Overview
TEAM-PEERLESS was tasked with developing a weather application that provides the weather data for current
date or dates in the past. Using a combination of two APIs, the program is able retrieve information such as temperature, windspeed, wind direction, and barometric pressure in both imperial and metric units. The application functions as a command line interface but also has a added graphic user interface that is extremely easy to use.

### How to Run the Program

1. Open your command line in the location of the AmesWeather.py application.
2. **Type:** python AmesWeather.py T
  - The T at the end will return the current temperature but we will go over all the other possible parameters you can put in place of it below.
3. As you learn the parameters, keep in mind that multiple parameters may be ran at the same time. Just leave a space between each one and they will be printed in the order you type them into the command line.

### Components

Below are listed the tools we used to complete this project:

##### Dark Sky API
This API provides current weather as well predictive forecasts up to 7 days out and forecasts from the past that go back decades. The API can be used 1000 times per day free of charge. All data is retrieved in JSON format.

https://darksky.net/dev/docs

##### APIXU
Similar to Dark Sky, APIXU retrieves weather data, including some bonuses such as astrology, which returns sunrise, sunset, moonrise, and moonset data.

https://www.apixu.com/api.aspx

##### Atom
The code was written using Atom text editor.

https://atom.io/

### Types of Parameters

Here will be all of the different types of parameters you will be able to run via command line, and what they will output, for the Ames Weather program.

- T - Current temperature
- P - Current air pressure
- WS - Current wind speed
- WD - Current wind direction
- Day/Week/Month/Year ago from current time:
 - -D - Returns either the temp, air pressure, wind speed, or wind direction from a day ago at this time. (ex. T-D returns the temperature from a day ago)
 - -W - Returns either the temp, air pressure, wind speed, or wind direction from a week ago at this time. (ex. P-W returns the air pressure from a week ago)
 - -M - Returns either the temp, air pressure, wind speed, or wind direction from a week ago at this time. (ex. WD-M returns the wind direction from a month ago)
 - -Y - Returns either the temp, air pressure, wind speed, or wind direction from a week ago at this time. (ex. WS-Y returns the wind speed from a year ago)
- --metric - Outputs are given in metric. (ex. --metric WS T-D returns the WS and yesterdays temperature in metric.)
  - Unless this is parameter is used, all outputs are in USCS.
- --time-offset=MM/DD/YYYY:HH:MM - This is used to display your own time and data for historical data. (ex. --time-offset=02/12/2015:17:37 --metric WS T T-D T-Y would return the wind speed, temperature, temperature from a day ago, and the temperature from a year ago. This would all be relative to the time offset, which in our case was February 2nd, 2015 at 5:37pm.)

### Calculations
Since the APIs provide the data in imperial format, conversions are needed to be able to display the information in metric units. Displayed information maybe 0.02-0.04 units off due to rounding. Listed below are the conversions used:

**Convert Fahrenheit to Celsius**

if convertTo == 'C':

return round(((5 / 9) * (temp - 32)), 1)

else:

return round(temp, 1)

**Convert to Kilometers per hour**

if convertTo == 'KMH':

return round(ws * 1.61, 1)

else:

return round(ws, 1)

**Convert to Inch of Mercury**

if convertTo == 'inHg':

return round(pr * 0.02953, 1)

else:

return round(pr, 1)

**Time Offset:** To account for daylight savings time when retrieving historical data, the application incorporates a timeOffset method that calculates the correct time.

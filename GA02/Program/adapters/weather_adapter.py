from chatterbot.logic import LogicAdapter
from requests import get
from time import sleep
from re import sub
from fuzzywuzzy import process
API_KEY = "949a7ca4395f4f1b9b6220440171902"
ZIP = "50014"
certainty = 90
directions = {'N': 'north',
              'S': 'south',
              'E': 'east',
              'W': 'west',
              'NE': 'northeast',
              'NW': 'northwest',
              'SE': 'southeast',
              'SW': 'southwest',
              'NNE': 'north-northeast',
              'ENE': 'east-northeast',
              'ESE': 'east-southeast',
              'SSE': 'south-southeast',
              'SSW': 'south-southwest',
              'WSW': 'west-southwest',
              'WNW': 'west-northwest',
              'NNW': 'north-northwest'}


class weather_adapter(LogicAdapter):

    def __init__(self, **kwargs):
        super(weather_adapter, self).__init__(**kwargs)

    def getTop(self, statement):
        #print("1: "+statement)
        choices = []
        words = ['temp', 'temperature', 'wind', 'speed', 'hot', 'cold', 'weather', 'whether']
        statement = [str(x.lower()) for x in statement.split(" ")]
        statement = [sub(r'\W+', '', x) for x in statement]
        #print(statement)
        for x in statement:
            y = process.extractOne(x, words)
            #print(y)
            if(y[1] > certainty):
                choices.append(y)
        choices.sort(key=lambda x: x[1], reverse=True)
        if len(choices) is 0:
            return ('Nope', -10)
        else:
            return(choices[0])

    def getData(self):
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

    def getTemperature(self, data, metric=False):
        """This returns the temperature from the weather data"""
        # checks if user wants metric or USCS
        if metric:
            # retrieves data
            data = data["current"]["temp_c"]
            # checks if data exists
            if data:
                # returns temperature in celcius
                return data
            else:
                # returns NA
                return "NA"
        else:
            # retrieves data
            data = self.getData()["current"]["temp_f"]
            # checks if data exists
            if data:
                # returns temperature in fahrenheit
                return data
            else:
                # returns NA
                return "NA"

    def getPressure(self, data, metric=False):
        """This returns the pressure from the weather data"""
        # checks if user wants metric or USCS
        if metric:
            # retrieves data
            data = data["current"]["pressure_mb"]
            # checks if data exists
            if data:
                # returns barometric pressure in millibars
                return data
            else:
                # returns NA
                return "NA"
        else:
            # retrieves data
            data = data["current"]["pressure_in"]
            # checks if data exists
            if data:
                # returns barometric pressure in inHg
                return data
            else:
                # returns NA
                return "NA"

    def getWindSpeed(self, data, metric=False):
        """This returns the wind speed from the weather data"""
        # checks if user wants metric or USCS
        if metric:
            # retrieves data
            data = data["current"]["wind_kph"]
            # checks if data exists
            if data:
                # returns wind speed in kph
                return data
            else:
                # returns NA
                return "NA"
        else:
            # retrieves data
            data = data["current"]["wind_mph"]
            # checks if data exists
            if data:
                # returns wind speed in mph
                return data
            else:
                # returns NA
                return "NA"

    def getWindDirection(self, data):
        """This returns the wind direction from the weather data"""
        # retrieves data
        data = data["current"]["wind_dir"]
        # checks if data exists
        if data:
            # returns wind direction
            return data
        else:
            # returns NA
            return "NA"

    def can_process(self, statement):
        full_statement = str(statement)
        top = self.getTop(full_statement)
        if 'horse' in full_statement:
            return False
        if top[1] > certainty:
            return True
        else:
            return False

    def getFeelsLike(self, data):
        data = data["current"]["feelslike_f"]
        if data:
            # returns feellke
            return data
        else:
            # returns NA
            return "NA"

    def getDesc(self, data):
        data = data["current"]["condition"]["text"]
        if data:
            # returns condition
            return data
        else:
            # returns NA
            return "NA"

    def process(self, statement):
        from chatterbot.conversation import Statement
        '''# Make a request to the temperature API'''
        full_statement = str(statement)
        top = self.getTop(full_statement)
        result = ''
        if top[1] > certainty:
            data = self.getData()
            temperature = self.getTemperature(data)
            wind = self.getWindSpeed(data)
            wd = self.getWindDirection(data)
            feelslike = self.getFeelsLike(data)
            condition = self.getDesc(data).lower()

            if temperature and wind and wd:
                confidence = 1
                result = 'It\'s currently ' + condition + ' and ' + str(temperature) + ' degrees outside, but it feels like ' + str(feelslike) + ' degrees. \n The wind is currently ' + str(wind) + ' mph coming from the ' + directions[wd] + '.'
            else:
                confidence = 0
        else:
            result = 'Hmm.. There seems to be a problem with my weather circuit! I\'ll phone the weather man.'

        response_statement = Statement(result)
        response_statement.confidence = confidence

        return response_statement

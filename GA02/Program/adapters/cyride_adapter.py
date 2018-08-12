from chatterbot.logic import LogicAdapter
from fuzzywuzzy import process
import xml.etree.ElementTree as ET
from urllib.request import urlopen
import time
import re

certainty = 90


class cyride_adapter(LogicAdapter):
    def __init__(self, **kwargs):
        super(cyride_adapter, self).__init__(**kwargs)

    def getTop(self, statement):
        '''Function to retreive the top matches, and their probability'''
        choices = []
        # words to check for match
        words = ['cyride', 'bus', 'stop']
        # strip punctuation
        statement = [x.lower() for x in str(statement).split()]
        statement = [re.sub(r'\W+', '', x) for x in statement]
        for x in statement:
            # Find the top matches
            y = process.extractOne(x, words)
            # If we are fairly certainty
            if(y[1] > certainty):
                # Add it to choices
                choices.append(y)
        # Sort it to have top at the front
        choices.sort(key=lambda x: x[1], reverse=True)
        if len(choices) is 0:
            return ('Nope', -10)
        else:
            return(choices[0])

    def getData(self, stopId):
        '''returns a json file with the bus info'''
        # URL for the API
        url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=cyride&stopId=%s' % (stopId)
        # Get the tree from the url
        tree = ET.ElementTree(file=urlopen(url))
        # Get the root
        root = tree.getroot()

        # Dictonary to hold all of the routes, with the route name as the key
        routes = {}
        # Navigate through each child in the predictions category
        for child in root.findall('predictions'):
            predictions = []
            # Add all of the predictions to the list
            for direction in child:
                for predict in direction:
                    # Add that prediction to the list
                    predictions.append(predict)
            # Finally associate those predictions with that route in the dictonary
            routes[child.attrib['routeTitle']] = predictions
        return routes

    def can_process(self, statement):
        '''Tests to see if the statement can be processed'''
        full_statement = str(statement)
        # Make sure we have cyride or bus, and a 4 digit bus stop
        # Check the top word match, and if it is above certainty percent, we run with it!
        if 'horse' in full_statement:
            return False
        top = self.getTop(full_statement)
        if top[1] > certainty:
            return True
        else:
            return False

    def process(self, statement):
        """Performs the process to get the statement"""
        full_statement = str(statement)
        # Check the top word match, and if it is above certainty percent, we run with it!
        top = self.getTop(full_statement)
        # If it is above the certainty
        if top[1] > certainty:
            # Make sure it has a bus stop number
            if len(re.findall(r'\d{4}', full_statement)) > 0:
                stopId = re.findall(r'\d{4}', full_statement)[0]
                routes = self.getData(stopId)
                # If there isnt any in the list, we ask them about the input
                if len(routes) is 0:
                    result = 'Hmm, there seems to be a problem. Are you sure that ' + str(stopId) + ' is actually a stop?'
                else:
                    # Otherwise we start the output
                    result = ""
                    result += ('There are ' + str(len(routes)) + ' route(s) that service stop ' + str(stopId) + ': ' + ', '.join(routes) + '' + '\n\n\n')
                    # Hold it to see if it is printed..
                    printed = False
                    for dic in routes:
                        for e in routes[dic]:
                            # Check to see if it is within 15 mins
                            if(int(e.attrib['minutes']) <= 15):
                                # then we append it to our list
                                printed = True
                                unix = e.attrib['epochTime']
                                unix = int(unix[:-3])
                                d = time.strftime('%I:%M %p', time.localtime(unix)).lstrip('0').replace(' 0', ' ')
                                result += ('Bus ' + dic + ' predicted time: ' + d + ' (' + e.attrib['minutes'] + ' minutes) \n')
                    # If its not printed, tell them there are no busses
                    if not printed:
                        result += ('There are currently no busses arriving within the next 15 minutes.')

            else:
                result = 'Hmm, it seems you didn\'t state a bus stop!'

            from chatterbot.conversation import Statement

            response_statement = Statement(result)
            response_statement.confidence = 1

            # print(result)
            return response_statement

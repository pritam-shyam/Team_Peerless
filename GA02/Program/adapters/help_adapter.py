from chatterbot.logic import LogicAdapter
import re
from fuzzywuzzy import fuzz
certainty = 85
helpresponse = "Sure! Here are a list of commands I have! \n" + "*Weather*: Ask me what the weather is like. I will tell you the wind speed, temperature, and what it feels like outside. \n" + "*Cyride*: Provide me with a bus top ID, and I can tell the busses arriving in the next 15 minutes \n" + "*HORSE*: Say 'horse play' to begin a game, and 'horse guess X' to guess a letter! \n" + "*Sports*: Provide me with 'nba/nhl/mlb/nfl scoreboard' and I can tell you the games today, and if they are in progress I can tell scores! \n" + "I can also show you the game schedule for your favorite team. say '<nba_team_here> schedule' to take a peek! \n \n" + "I hope you enjoy having me around!"

replies = {'What can you do?': helpresponse,
           'Help': helpresponse,
           'What commands do you have?': helpresponse,
           'Can you help me?': helpresponse}


class help_adapter(LogicAdapter):

    def __init__(self, **kwargs):
        super(help_adapter, self).__init__(**kwargs)

    def can_process(self, statement):
        '''Tests to see if the statement can be processed'''
        top = getTop(statement)
        # If the certainty of the tuple is above the set certainty
        if top[1] > certainty:
            # then we can process
            return True
        else:
            return False

    def process(self, statement):
        '''Performs the process to get the statement'''
        from chatterbot.conversation import Statement

        top = getTop(statement)
        # If the certainty of the tuple is above the set certainty
        if(top[1] > certainty):
            # Make that reply the response
            bot_response = replies[top[0]]

        response_statement = Statement(bot_response)
        response_statement.confidence = 1
        return response_statement


def getTop(statement):
    """Function to retreive the top matches, and their probability"""
    choices = []
    words = replies.keys()
    words = list(words)
    # Strip it
    statement = [x.lower() for x in str(statement).split()]
    statement = [re.sub(r'\W+', '', x) for x in statement]
    # make it a str again
    statement = ' '.join(statement[1::])
    for x in words:
        # Find the probability of match
        y = fuzz.token_sort_ratio(statement, x)
        # if y is above certainty, append that
        if(y > certainty):
            choices.append((x, y))
    choices.sort(key=lambda x: x[1], reverse=True)
    if len(choices) is 0:
        # if there are no choices, return this no
        return ('Nope', -10)
    else:
        return(choices[0])

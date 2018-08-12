from chatterbot.logic import LogicAdapter
import re
from fuzzywuzzy import fuzz
certainty = 85
replies = {'What is your mother tongue?': '01000010 01101001 01101110 01100001 01110010 01111001 00101100 00100000 01101111 01100110 00100000 01100011 01101111 01110101 01110010 01110011 01100101 00100001',
           'Are you with the NSA?': 'I can neither confirm, nor deny the existance of a bugging software in this bot.',
           'Who is your father?': 'You mean my dad? Great old Monty.',
           'How were you made?': 'You see, when a CPU and a motherboard love each other very much. . .',
           'Hide dead body': 'Quick, drag it to the recycle bin on your desktop!',
           'What group is the best?': 'Gee, I dont know.. Check the GA1 scores.'}


class easteregg_adapter(LogicAdapter):

    def __init__(self, **kwargs):
        super(easteregg_adapter, self).__init__(**kwargs)

    def can_process(self, statement):
        """Tests to see if the statement can be processed"""
        top = getTop(statement)
        # If the certainty of the tuple is above the set certainty
        if top[1] > certainty:
            # then we can process
            return True
        else:
            return False

    def process(self, statement):
        """Performs the process to get the statement"""
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

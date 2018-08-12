from chatterbot.logic import LogicAdapter
import random
import re


class greetings_adapter(LogicAdapter):


    def __init__(self, **kwargs):
        super(greetings_adapter, self).__init__(**kwargs)

    def can_process(self, statement):
        statement = [x.lower() for x in statement.text.split()]
        statement = [re.sub(r'\W+', '', x) for x in statement]

        greeting_keywords = ("hello", "hi", "greetings", "sup", "what's up",)

        if any(x.lower() in statement for x in greeting_keywords):
            return True
        else:
            return False

    def process(self, statement):
        from chatterbot.conversation import Statement
        import requests

        greeting_responses = ["Hi! I'm CyBot!", "*nods*", "Hello human."]
        bot_response = random.choice(greeting_responses)
        response_statement = Statement(bot_response)
        response_statement.confidence = 1

        return response_statement

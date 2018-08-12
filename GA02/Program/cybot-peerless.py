from slackclient import SlackClient
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot import ChatBot
import time
import os
import logging
import re
import subprocess

# var constants
BOT_ID = "U4B6UN2AD"
API_KEY = 'xoxb-147232750353-0Udkb21xAhlHPJ6PtN5Z6Xss'
slack_client = SlackClient(API_KEY)
AT_BOT = "<@" + BOT_ID + ">"
PID_FILENAME = "chatbotid.txt"
PID_FILENAME = "/home/peerless/TEAM-PEERLESS/GA02/Program/logging/cybot.PID"
# PID_FILENAME = "D:/Jinkoo/Desktop/Local Repositories/TEAM-PEERLESS/GA02/Program/logging/cybot.PID"

# init logging
#logging.basicConfig(filename='.\logging\cybot.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p')


# init chatterbot chatbot
cybot = ChatBot(
    "cybot-peerless",
    # hide json db warning
    silence_performance_warning=True,
    # use json db
    storage_adapter="chatterbot.storage.JsonFileStorageAdapter",
    # add custom logic adapters in order and some settings
    logic_adapters=[
        {
            "import_path": "adapters.greetings_adapter.greetings_adapter"
        },
        {
            "import_path": "adapters.cyride_adapter.cyride_adapter"
        },
        {
            "import_path": "adapters.easteregg_adapter.easteregg_adapter"
        },
        {
            "import_path": "adapters.weather_adapter.weather_adapter"
        },
        {
            "import_path": "adapters.sports_adapter.sports_adapter"
        },
        {
            "import_path": "adapters.help_adapter.help_adapter"
        },
        {
            "import_path": "adapters.horse_adapter.horse_adapter"
        },
        {
            "import_path": "chatterbot.logic.BestMatch",
            "statement_comparison_function": "chatterbot.comparisons.synset_distance",
            "response_selection_method": "chatterbot.response_selection.get_first_response"
        }
    ],
    database="./database.json",
    filters=["chatterbot.filters.RepetitiveResponseFilter"]
)


def handle_command(message, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    bot_input = ''

    try:
        bot_input = cybot.get_response(message)
        slack_client.rtm_send_message(channel, str(bot_input))
    except(KeyboardInterrupt, EOFError, SystemExit):
        logging.error("There has been an error.")


def parse_slack_output(slack_rtm_output):
    """returns message, user, channel, ts"""
    # create vars
    message, user, channel, ts = '', '', '', ''
    # get output
    output_list = slack_rtm_output
    # check if anything in output
    if output_list and len(output_list) > 0:
        # iterate through output
        for output in output_list:
            # assign data to vars
            if 'text' in output:
                message = output['text']
            if 'user' in output:
                user = output['user']
            if 'channel' in output:
                channel = output['channel']
            if 'ts' in output:
                ts = output['ts']
    # return vars
    return message, user, channel, ts


def delete_db():
    """This deletes the database.json to delete any learned responses"""
    # get current time
    now = time.time()
    # get current working directory
    dir_to_search = os.getcwd()
    # set file path to database.json
    file_path_db = os.path.join(dir_to_search+"/database.json")

    # attempt to remove database.json
    try:
        # delete database.json
        os.remove(str(file_path_db))
        # print sucessful
        logging.info("Deleted database.json")
    except:
        # print deletion error
        logging.error("Could not delete database.json")
        # pass exception
        pass


def isChatBotRunning(fileName):
    try:
        f = open(fileName)
        pid = str(f.read())
    except:
        return False  # if we can't open the file or read valid data, then no

    ps = subprocess.Popen("ps -e | grep " + pid , shell=True, stdout=subprocess.PIPE)
    output = ps.stdout.read().decode('utf-8')
    ps.stdout.close()
    ps.wait()
    if re.search(pid, output) is None:
        return False # PID was not found
    else:
        return True


if __name__ == "__main__":
    """Main function"""
    if isChatBotRunning(PID_FILENAME):
        logging.info("Cybot Start Attempt: Cybot is running.")
    else:
        logging.info("Cybot Start Attempt: Cybot is not running and will be started")
        try:
            f = open(PID_FILENAME, 'w')
            f.write(str(os.getpid()))
            f.close()
        except:
            logging.error("We couldn't open the file for writing PID, therefore cannot start")
            quit()
        # delay for slack communications
        READ_WEBSOCKET_DELAY = 1
        # delete database.json
        delete_db()
        # set trainer
        cybot.set_trainer(ChatterBotCorpusTrainer)
        # train chatbot
        cybot.train(
            "chatterbot.corpus.english.greetings",
            "chatterbot.corpus.english.conversations"
        )
        # check if connection is available
        if slack_client.rtm_connect():
            # print that connection is available
            logging.info("Cybot connected and running!")
            # always check for message
            while True:
                # set vars from parse function
                message, user, channel, ts = parse_slack_output(slack_client.rtm_read())
                # check if vars exist
                if message and user and channel:
                    # if bot is mentioned
                    if AT_BOT in message:
                        # handle vars
                        handle_command(message, channel, user)
                        # sleep before checking again
                        time.sleep(READ_WEBSOCKET_DELAY)
        # if slack connection isn't available
        else:
            # print error
            print("Connection failed. Invalid Slack token or bot ID?")
            logging.error("Connection failed. Invalid Slack token or bot ID?")

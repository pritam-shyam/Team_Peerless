from chatterbot.logic import LogicAdapter
import base64
from requests import get, exceptions
from random import choice
from sys import exc_info
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import datetime
import json
from pickle import load, dump
from os import getcwd, path, stat, remove, listdir
from time import time


class sports_adapter(LogicAdapter):

    def __init__(self, **kwargs):
        """Initializes sports adapter with authentication variables"""
        # Pass through args to LogicAdapter class
        super(sports_adapter, self).__init__(**kwargs)
        # Make a tuple with auth credentials
        username = "TREINERT"
        password = "TEAM-PEERLESS"
        self.auth = (username, password)

    def to_local_time(self, timestr):
        """Change EST tz string to CST tz string"""
        # Split the given time string
        parts = timestr.split(':')
        min = parts[1][0:2]
        desc = parts[1][2::]
        hour = parts[0]
        # Get the hour part, and adjust to current time.
        # This code deals with the AM/PM switch, and midnight/noon
        if hour is '12':
            hour = '11'
            if desc is 'AM':
                desc = 'PM'
            else:
                desc = 'AM'
        elif hour is '1':
            hour = '12'
        else:
            hour = int(hour) - 1

        # concat into format needed
        result = str(hour) + ':' + str(min) + str(desc)
        # Return fixed time.
        return(result)

    def check_cache_date(self):
        """Checks cache file, dates, and deletes all files seven days or older"""
        # get the current time
        now = time()
        # get the 3 days before
        cutoff = now - (3 * 86400)
        # get the current working directory string
        cwd = getcwd()

        # get the file path to the cache folder from cwd
        file_path = path.join(cwd, "sports_data/nba/")
        # get a list of all the files in the cache folder
        files = listdir(path.join(cwd, "sports_data/nba/"))

        # iterate through files in cache folder
        for xfile in files:
            # check if the file exists
            if path.isfile(str(file_path) + xfile):
                # get different statistics about the file
                t = stat(str(file_path) + xfile)
                # get time of most recent metadata change of file
                c = t.st_ctime
                # check if file older than 3 days
                if c < cutoff:
                    # delete cached file
                    remove(str(file_path) + xfile)

    def get_nba_full_game_schedule(self):
        """Retrieves full nba schedule"""
        # get todays date in string form
        today = datetime.date.today().strftime("%Y%m%d")

        # base response for fall back
        response = "Sorry, couldn't get the schedule."

        # make boolean for cache check
        hasFile = False

        # attempt to load cache file
        try:
            # store cached file
            file = load(open("sports_data/nba/nba_full_game_schedule_" + today + ".p", "rb"))
            # set bool to true
            hasFile = True
        # if file did not exist
        except FileNotFoundError:
            # set bool to false
            hasFile = False
            # pass the exception
            pass

        # if cache exists
        if hasFile:
            # return stored schedule object
            return file
        # if cache does not exist
        else:
            # attempt api request of the latest nba full game schedule
            try:
                # get info from api source
                response = get(
                    url="https://www.mysportsfeeds.com/api/feed/pull/nba/latest/full_game_schedule.json",
                    auth=self.auth
                )
                # make json object with easily iterable schedule
                data = response.json()['fullgameschedule']['gameentry']
                # store game schedule with todays date for cache
                dump(data, open("sports_data/nba/nba_full_game_scheudle_" + today + ".p", "wb"))
                # return json object
                return response.json()['fullgameschedule']['gameentry']
            # catch api exceptions
            except exceptions.RequestException:
                # print if api request fails
                print('HTTP Request failed')
        # return response
        return response

    def get_nba_daily_scores(self, date):
        """Retreives nba daily scores per day"""
        # base response for fall back
        response = "Sorry, couldn't get the schedule"

        # make boolean for cache check
        hasFile = False
        # attempt to load cache file
        try:
            # store cached file
            file = load(open("sports_data/nba/nba_daily_scores_" + date + ".p", "rb"))
            # set bool to true
            hasFile = True
        # if file did not exist
        except FileNotFoundError:
            # set bool to false
            hasFile = False
            # pass the exception
            pass

        # if cache exists
        if hasFile:
            # return stored schedule object
            return file
        # if cache does not exist
        else:
            try:
                # attempt api request of daily nba scores
                response = get(
                    url="https://www.mysportsfeeds.com/api/feed/pull/nba/2016-2017-regular/scoreboard.json?fordate=" + date,
                    auth=self.auth
                )
                # make json object with easily iterable schedule
                data = response.json()['scoreboard']['gameScore']
                # store daily nba scores with todays date for cache
                dump(data, open("sports_data/nba/nba_daily_scores_" + date + ".p", "wb"))
                # return json object
                return response.json()['scoreboard']['gameScore']
            # catch api exceptions
            except exceptions.RequestException:
                # print if api request fails
                print('HTTP Request failed')
        # return response
        return response

    def get_nba_scores_by_date_id(self, game_id, game_date):
        """Finds nba score from daily schedule from full schedule"""
        # convert date object to string
        game_date = game_date.strftime("%Y%m%d")

        # get nba daily scores for the date provided
        scores = self.get_nba_daily_scores(game_date)

        # get todays date in a string
        today = datetime.date.today().strftime("%Y%m%d")

        # base response
        response = "Sorry, couldn't get the scores"

        # make boolean for cache check
        hasFile = False
        # attempt to load cache file
        try:
            # store cached file
            file = load(open("sports_data/nba/nba_game_score_" + game_date + "_" + game_id + ".p", "rb"))
            # set bool to true
            hasFile = True
        # if file did not exist
        except FileNotFoundError:
            # set bool to false
            hasFile = False
            # pass the exception
            pass

        # if cache exists
        if hasFile:
            # return stored schedule object
            return file
        # if cache does not exist
        else:
            # iterate through the daily scores
            for i in range(0, len(scores)):
                # try store score cache and return score
                try:
                    # check if id is in json
                    id = scores[i]['game']['ID']
                    # check if ids match from passed through id and daily scores
                    if str(game_id) == str(id):
                        # define object
                        data = str("*" + scores[i]['awayScore'] + "-" + scores[i]['homeScore'] + " FINAL*")
                        # store object
                        dump(data, open("sports_data/nba/nba_game_score_" + game_date + "_" + id + ".p", "wb"))
                        # return object
                        return str("*" + scores[i]['awayScore'] + "-" + scores[i]['homeScore'] + " FINAL*")
                # if id not found or any other error
                except:
                    # pass any exceptions
                    pass
        # if nothing was returned then return a blank string
        return ""

    def get_nba_team_schedule(self, team):
        """Retreives team schedule response"""
        # run cache check for schedule data
        self.check_cache_date()

        # base responses
        res = ""
        response = "Sorry, could not retrieve the NBA game schedule."

        # todays date in string format
        today = datetime.date.today().strftime("%Y%m%d")

        # make boolean for cache check
        hasFile = False
        # attempt to load cache file
        try:
            # store cached file
            file = load(open("sports_data/nba/nba_" + team + "_" + today + ".p", "rb"))
            # set bool to true
            hasFile = True
        # if file did not exist
        except FileNotFoundError:
            # set bool to false
            hasFile = False
            # pass the exception
            pass

        # if cache exists
        if hasFile:
            # return stored schedule object
            return file
        # if cache does not exist
        else:
            # attempt to retrieve team schedule from api
            try:
                # current date
                todays_date = datetime.date.today()
                # current date - 7 days
                left_range = todays_date + datetime.timedelta(days=-7)
                # current date + 7 days
                right_range = todays_date + datetime.timedelta(days=7)
                # retrieve full game schedule
                team_schedule = self.get_nba_full_game_schedule()
                # if full team schedule exists
                if team_schedule:
                    # if team was pass through
                    if team:
                        # add title to res
                        res = "*"+team+" Schedule* "+left_range.strftime("%m/%d/%y")+"-"+right_range.strftime("%m/%d/%y")+" :basketball:\n"
                        # iterate through full team schedule
                        for i in range(0, len(team_schedule)):
                            # set variables for multiple info
                            home_team = team_schedule[i]['homeTeam']['Name']
                            away_team = team_schedule[i]['awayTeam']['Name']
                            home_city = team_schedule[i]['homeTeam']['City']
                            away_city = team_schedule[i]['awayTeam']['City']

                            # created date object for game date from string
                            game_date = datetime.datetime.strptime(team_schedule[i]['date'], "%Y-%m-%d").date()

                            # game start time string
                            game_start_time = team_schedule[i]['time']

                            # check if the game is between the 7 days before and after today
                            if left_range <= game_date <= right_range:
                                # if game is before today
                                if game_date < todays_date:
                                    # get game id
                                    game_id = team_schedule[i]['id']

                                    # return scores for specific date and game
                                    scores_str = self.get_nba_scores_by_date_id(game_id, game_date)

                                    # check if team is home
                                    if home_team == team:
                                        # add game str to res
                                        res += str("*"+game_date.strftime("%m/%d/%y")+" "+game_start_time+"* "+away_city+" "+away_team+" @ _"+home_city+" "+home_team+"_ "+scores_str+"\n")
                                    # check if team is away
                                    elif away_team == team:
                                        # add game str to res
                                        res += str("*"+game_date.strftime("%m/%d/%y")+" "+game_start_time+"* _"+away_city+" "+away_team+"_ @ "+home_city+" "+home_team+" "+scores_str+"\n")
                                # if game is today
                                elif game_date == todays_date:
                                    # check if team is home
                                    if home_team == team:
                                        # add game str to res
                                        res += str("*"+game_date.strftime("%m/%d/%y")+" "+game_start_time+"* "+away_city+" "+away_team+" @ "+home_city+" "+home_team+" *SB*\n")
                                    # check if team is away
                                    elif away_team == team:
                                        # add game str to res
                                        res += str("*"+game_date.strftime("%m/%d/%y")+" "+game_start_time+"* "+away_city+" "+away_team+" @ "+home_city+" "+home_team+" *SB*\n")
                                # if game is after today
                                else:
                                    # check if team is home
                                    if home_team == team:
                                        # add game str to res
                                        res += str("*"+game_date.strftime("%m/%d/%y")+" "+game_start_time+"* "+away_city+" "+away_team+" @ "+home_city+" "+home_team+" *TBD*\n")
                                    # check if team is away
                                    elif away_team == team:
                                        # add game str to res
                                        res += str("*"+game_date.strftime("%m/%d/%y")+" "+game_start_time+"* "+away_city+" "+away_team+" @ "+home_city+" "+home_team+" *TBD*\n")
                            # store object
                            dump(res, open("sports_data/nba/nba_"+team+"_"+today+".p", "wb" ) )
                        # return response
                        return res
                    # if schedule doesn't exist
                    else:
                        # return response
                        return "Sorry, couldn't get the schedule."
            # catch any exceptions
            except:
                # print error
                print("Unexpected error:", exc_info()[0])
                # raise exception
                raise
            # return response
            return response


    def get_nba_scoreboard_data(self):
        """Get NBA scoreboard data"""
        # get todays date
        date = datetime.date.today()
        # attempt to retreive data and return it
        try:
            response = get(
                url="https://www.mysportsfeeds.com/api/feed/pull/nba/latest/scoreboard.json?fordate="+date.strftime("%Y%m%d"),
                auth=self.auth
            )
            return response.json()['scoreboard']['gameScore']
        # catch request exception
        except exceptions.RequestException:
            # print error
            print('HTTP Request failed')


    def get_nhl_scoreboard_data(self):
        """Get NHL scoreboard data"""
        # get todays date
        date = datetime.date.today()
        # attempt to retreive data and return it
        try:
            response = get(
                url="https://www.mysportsfeeds.com/api/feed/pull/nhl/latest/scoreboard.json?fordate="+date.strftime("%Y%m%d"),
                auth=self.auth
            )
            return response.json()['scoreboard']['gameScore']
        # catch request exception
        except exceptions.RequestException:
            # print error
            print('HTTP Request failed')


    def get_nba_scoreboard_response(self):
        """Retreives scoreboard response"""
        # base response
        response = "Sorry, it seems the NBA has been assimilated."
        # initialize extra responses var
        extra_responses =[""]
        # attempt to create nba scoreboard response
        try:
            # get data from cache or api
            current_day_games = self.get_nba_scoreboard_data()

            # add title to response
            response = "*NBA Games of "+ datetime.date.today().strftime("%m/%d/%Y") +"* :basketball:\n"

            # iterate through daily scores data
            for i in range(0, len(current_day_games)):
                    # set variables for multiple info
                    home_team = current_day_games[i]['game']['homeTeam']['Name']
                    away_team = current_day_games[i]['game']['awayTeam']['Name']
                    home_city = current_day_games[i]['game']['homeTeam']['City']
                    away_city = current_day_games[i]['game']['awayTeam']['City']
                    game_start_time = current_day_games[i]['game']['time']
                    game_start_time = self.to_local_time(game_start_time)

                    is_in_progress = current_day_games[i]['isInProgress']
                    is_completed = current_day_games[i]['isCompleted']
                    is_unplayed = current_day_games[i]['isUnplayed']

                    # check if game is in progress
                    if is_in_progress in ['true']:
                        # set variables for team scores
                        home_score = current_day_games[i]['homeScore']
                        away_score = current_day_games[i]['awayScore']

                        # attempt to return a quarter and score for the game
                        try:
                            # check if keys exist
                            if current_day_games[i]['currentQuarter'] and current_day_games[i]['currentQuarterSecondsRemaining']:
                                # set variable current quarter
                                current_quarter = current_day_games[i]['currentQuarter']

                                # set variable to seconds remaining
                                seconds_rem_current_quarter = int(current_day_games[i]['currentQuarterSecondsRemaining'])

                                # seperated seconds to minutes and seconds
                                m, s = divmod(seconds_rem_current_quarter, 60)
                                # casting and formatting
                                m = str(m)
                                s = "%02d" % (s,)

                                # create int vars of scores
                                home_int = int(home_score)
                                away_int = int(away_score)

                                # placeholder for winning team
                                winner = ""
                                # check if home is winning
                                if home_int > away_int:
                                    # set winning team to home
                                    winner = "home"
                                # check if away is winning
                                elif home_int < away_int:
                                    # set winning team to away
                                    winner = "away"

                                # check if winning team is the home team
                                if winner == "home":
                                    # add properly formatted game string to response
                                    response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ _" + home_city +" "+home_team+"_ *"+away_score+"-"+home_score+" Q"+current_quarter+" "+m+":"+s)+"*\n"
                                    # add an extra response to list
                                    extra_responses.append(str("\nThe " + home_city +" "+home_team+" are winning!"))
                                # check if winning team is the away team
                                elif winner == "away":
                                    # add properly formatted game string to response
                                    response += str("*"+game_start_time+"* _"+away_city+" "+away_team + "_ @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score+" Q"+current_quarter+" "+m+":"+s)+"*\n"
                                    # add an extra response to list
                                    extra_responses.append(str("\nThe " + away_city +" "+away_team+" are winning!"))
                                # teams are tied
                                else:
                                    # add properly formatted game string to response
                                    response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score+" Q"+current_quarter+" "+m+":"+s)+"*\n"
                                    # add an extra response to list
                                    extra_responses.append(str("\nThe "+home_city+" "+home_team + " and the " + away_city +" "+away_team+" are tied!"))
                            # if current quarter and seconds remaining do not exist
                            else:
                                # add properly formatted game string to response
                                response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score)+"*\n"
                        # if there is a key error with current quarter and seconds remaining
                        except KeyError:
                            # pass the exception as nothing has been added
                            pass
                    # check if all three conditions are false (reason for this is the api is crowdsourced and doesn't get updated right away and causes problems, same as isComplete)
                    elif is_unplayed in ['false'] and is_in_progress in ['false'] and is_completed in ['false']:
                        # check if scores exist
                        if current_day_games[i]['awayScore'] and current_day_games[i]['homeScore']:
                            # set score vars
                            home_score = current_day_games[i]['homeScore']
                            away_score = current_day_games[i]['awayScore']
                            # create int version of score vars
                            home_int = int(home_score)
                            away_int = int(away_score)

                            # create winner place holder
                            winner = ""
                            # check if the home team won
                            if home_int > away_int:
                                # set winner to home team
                                winner = "home"
                            # check if the away team won
                            elif home_int < away_int:
                                # set winner to away team
                                winner = "away"

                            # check if the winner is the home team
                            if winner == "home":
                                # add properly formatted game string to response
                                response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ _" + home_city +" "+home_team+"_ *"+away_score+"-"+home_score)+" Final*\n"
                                # add extra responses bases on condition
                                extra_responses.append(str("\nWow! The "+home_city+" "+home_team+" won!"))
                                extra_responses.append(str("\nThe "+away_city+" "+away_team+" lost. :cry:"))
                            # check if the winner is the away team
                            elif winner == "away":
                                # add properly formatted game string to response
                                response += str("*"+game_start_time+"* _"+away_city+" "+away_team + "_ @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score)+" Final*\n"
                                # add extra responses bases on condition
                                extra_responses.append(str("\nHmmm looks like " + away_city +" "+away_team+" won!"))
                                extra_responses.append(str("\nThe "+home_city+" "+home_team+" lost."))
                            # if tied (shouldn't happen but safe)
                            else:
                                # add properly formatted game string to response
                                response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score)+" Final*\n"
                                # add extra responses based on condition
                                extra_responses.append(str("\nThe "+home_city+" "+home_team + " and the " + away_city +" "+away_team+" are tied!"))
                                extra_responses.append(str("\nThe "+away_city+" "+away_team + " and the " + home_city +" "+home_team+" are tied!"))
                    # check if game is complete
                    elif is_completed in ['true']:
                        # set score vars
                        home_score = current_day_games[i]['homeScore']
                        away_score = current_day_games[i]['awayScore']
                        # cast int score vars
                        home_int = int(home_score)
                        away_int = int(away_score)

                        # create winning team placeholder
                        winner = ""
                        # check if the home team won
                        if home_int > away_int:
                            # set winner to home
                            winner = "home"
                        # check if the away team won
                        elif home_int < away_int:
                            # set winner to away
                            winner = "away"

                        # check if the home team won
                        if winner == "home":
                            # add properly formatted game string to response
                            response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ _" + home_city +" "+home_team+"_ *"+away_score+"-"+home_score)+" Final*\n"
                            # add extra responses based on condition
                            extra_responses.append(str("\nWow! The "+home_city+" "+home_team+" won!"))
                            extra_responses.append(str("\nThe "+away_city+" "+away_team+" lost. :S"))
                        # check if the away team won
                        elif winner == "away":
                            # add properly formatted game string to response
                            response += str("*"+game_start_time+"* _"+away_city+" "+away_team + "_ @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score)+" Final*\n"
                            # add extra responses based on condition
                            extra_responses.append(str("\nWow! The "+away_city+" "+away_team+" won!"))
                            extra_responses.append(str("\nThe "+home_city+" "+home_team+" lost. :$"))
                        # score is tied (games don't end on ties)
                        else:
                            # add properly formatted game string to response
                            response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score)+" Final*\n"
                    # check if game is unplayed
                    elif is_unplayed in ['true']:
                        # add properly formatted game string to response
                        response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ " + home_city +" "+home_team)+" *TBD*\n"
                        # add extra responses based on condition
                        extra_responses.append(str("\nThe "+home_city+" "+home_team + " and the " + away_city +" "+away_team+" are playing today!"))
                        extra_responses.append(str("\nThe "+away_city+" "+away_team + " and the " + home_city +" "+home_team+" are playing later today! :smile:"))
                    # check for any other type (shouldn't have more)
                    else:
                        # add properly formatted game string to response
                        response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ " + home_city +" "+home_team)+" *TBD*\n"

            # add an extra_response randomly
            response += "\n"+choice(extra_responses)
            # return response
            return response
        # if there is an error
        except:
            # print error
            print("Unexpected error:", exc_info()[0])
            # raise error
            raise
        # return response
        return response


    def get_nhl_scoreboard_response(self):
        """Get NHL scoreboard response"""
        # base response
        response = "Sorry, it seems the NHL has been assimilated."
        # initialize extra responses var
        extra_responses = []
        # attempt to create nhl scoreboard response
        try:
            # get data from cache or api
            current_day_games = self.get_nhl_scoreboard_data()
            # add title string to response
            response = "*NHL Games of "+ datetime.date.today().strftime("%m/%d/%Y") +"* :ice_hockey_stick_and_puck:\n"
            # iterate through daily game data
            for i in range(0, len(current_day_games)):
                    # set vars for multiple info
                    home_team = current_day_games[i]['game']['homeTeam']['Name']
                    away_team = current_day_games[i]['game']['awayTeam']['Name']
                    home_city = current_day_games[i]['game']['homeTeam']['City']
                    away_city = current_day_games[i]['game']['awayTeam']['City']
                    game_start_time = current_day_games[i]['game']['time']
                    # convert timezone from est to cst
                    game_start_time = self.to_local_time(game_start_time)

                    # set vars for game states
                    is_in_progress = current_day_games[i]['isInProgress']
                    is_completed = current_day_games[i]['isCompleted']
                    is_unplayed = current_day_games[i]['isUnplayed']

                    # check if game is in progress
                    if is_in_progress in ['true']:
                        # set score vars
                        home_score = current_day_games[i]['homeScore']
                        away_score = current_day_games[i]['awayScore']
                        # attempt and return response
                        try:
                            # check if current period and seconds remaining are available
                            if current_day_games[i]['currentPeriod'] and current_day_games[i]['currentPeriodSecondsRemaining']:
                                # set vars for current period and seconds remaining in period
                                current_period = current_day_games[i]['currentPeriod']
                                seconds_rem_current_period = int(current_day_games[i]['currentPeriodSecondsRemaining'])
                                # split seconds into minutes and seconds
                                m, s = divmod(seconds_rem_current_period, 60)
                                # casting and formatting
                                m = str(m)
                                s = "%02d" % (s,)

                                # create new vars of scores in int
                                home_int = int(home_score)
                                away_int = int(away_score)

                                # create placeholder for winning team
                                winner = ""
                                # check if home team is winning
                                if home_int > away_int:
                                    # set winning team to home
                                    winner = "home"
                                # check if away team is winning
                                elif home_int < away_int:
                                    # set winning team to away
                                    winner = "away"

                                # check if the home team is winning
                                if winner == "home":
                                    # add properly formatted string to response
                                    response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ _" + home_city +" "+home_team+"_ *"+away_score+"-"+home_score+" Q"+current_period+" "+m+":"+s)+"*\n"
                                    # add extra responses based on condition
                                    extra_responses.append(str("\nThe " + home_city +" "+home_team+" are winning!"))
                                # check if the away team is winning
                                elif winner == "away":
                                    # add properly formatted string to response
                                    response += str("*"+game_start_time+"* _"+away_city+" "+away_team + "_ @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score+" Q"+current_period+" "+m+":"+s)+"*\n"
                                    # add extra responses based on condition
                                    extra_responses.append(str("\nThe " + away_city +" "+away_team+" are winning!"))
                                # check if the teams are tied
                                else:
                                    # add properly formatted string to response
                                    response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score+" Q"+current_period+" "+m+":"+s)+"*\n"
                                    # add extra responses based on condition
                                    extra_responses.append(str("\nThe "+home_city+" "+home_team + " and the " + away_city +" "+away_team+" are tied!"))
                            # if current period and seconds remaining do not exist
                            else:
                                # add properly formatted string to response
                                response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score)+"*\n"
                        # if there is a key error with current quarter and seconds remaining
                        except KeyError:
                            # add to response nothing
                            response += ""
                            # pass exception as time wasn't found
                            pass
                    # check if all three conditions are false (reason for this is the api is crowdsourced and doesn't get updated right away and causes problems, same as isComplete)
                    elif is_unplayed in ['false'] and is_in_progress in ['false'] and is_completed in ['false']:
                        # check if team scores exist
                        if current_day_games[i]['awayScore'] and current_day_games[i]['homeScore']:
                            # create team score vars
                            home_score = current_day_games[i]['homeScore']
                            away_score = current_day_games[i]['awayScore']
                            # create int vars of team scores
                            home_int = int(home_score)
                            away_int = int(away_score)

                            # create placeholder for winner
                            winner = ""
                            # check if home team won
                            if home_int > away_int:
                                # set winning team to home
                                winner = "home"
                            # check if away team won
                            elif home_int < away_int:
                                # set winning team to away
                                winner = "away"

                            # check if home team won
                            if winner == "home":
                                # add properly formatted string to response
                                response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ _" + home_city +" "+home_team+"_ *"+away_score+"-"+home_score)+" Final*\n"
                                # add extra responses based on condition
                                extra_responses.append(str("\nWow! The "+home_city+" "+home_team+" won!"))
                                extra_responses.append(str("\nThe "+away_city+" "+away_team+" lost. :("))
                            # check if away team won
                            elif winner == "away":
                                # add properly formatted string to response
                                response += str("*"+game_start_time+"* _"+away_city+" "+away_team + "_ @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score)+" Final*\n"
                                # add extra responses based on condition
                                extra_responses.append(str("\nWow! The "+away_city+" "+away_team+" won!"))
                                extra_responses.append(str("\nThe "+home_city+" "+home_team+" lost. :$"))
                            # score is tied (games don't end on ties)
                            else:
                                # add properly formatted string to response
                                response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score)+" Final*\n"
                    # check if game is complete
                    elif is_completed in ['true']:
                        # create team score vars
                        home_score = current_day_games[i]['homeScore']
                        away_score = current_day_games[i]['awayScore']
                        # create int vars of team scores
                        home_int = int(home_score)
                        away_int = int(away_score)

                        # create placeholder for winner
                        winner = ""
                        # check if the home team won
                        if home_int > away_int:
                            # set winning team to home
                            winner = "home"
                        # check if the away team won
                        elif home_int < away_int:
                            # set winning team to away
                            winner = "away"

                        # check if the home team won
                        if winner == "home":
                            # add properly formatted string to response
                            response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ _" + home_city +" "+home_team+"_ *"+away_score+"-"+home_score)+" Final*\n"
                            # add extra responses based on condition
                            extra_responses.append(str("\nWow! The "+home_city+" "+home_team+" won!"))
                            extra_responses.append(str("\nThe "+away_city+" "+away_team+" lost. :("))
                        # check if the away team won
                        elif winner == "away":
                            # add properly formatted string to response
                            response += str("*"+game_start_time+"* _"+away_city+" "+away_team + "_ @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score)+" Final*\n"
                            # add extra responses based on condition
                            extra_responses.append(str("\nWow! The "+away_city+" "+away_team+" won!"))
                            extra_responses.append(str("\nThe "+home_city+" "+home_team+" lost. :$"))
                        else:
                            # add properly formatted string to response
                            response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ " + home_city +" "+home_team+" *"+away_score+"-"+home_score)+" Final*\n"
                    # check if game is unplayed
                    elif is_unplayed in ['true']:
                        # add properly formatted string to response
                        response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ " + home_city +" "+home_team)+" *TBD*\n"
                        # add extra responses based on condition
                        extra_responses.append(str("\nThe "+home_city+" "+home_team + " and the " + away_city +" "+away_team+" are playing today!"))
                        extra_responses.append(str("\nThe "+away_city+" "+away_team + " and the " + home_city +" "+home_team+" are playing later today! :)"))
                    # score is tied (games don't end on ties)
                    else:
                        # add properly formatted string to response
                        response += str("*"+game_start_time+"* "+away_city+" "+away_team + " @ " + home_city +" "+home_team)+" *TBD*\n"
            # add random extra response to end of statment
            response += "\n"+choice(extra_responses)
            # return statement
            return response
        # if any error
        except:
            # print error
            print("Unexpected error:", exc_info()[0])
            # raise exception
            raise
        return response


    def get_mlb_scoreboard_response(self):
        """Get MLB scoreboard response"""
        # set mlb scoreboard response
        response = "Sorry, it seems the MLB is not in season. :baseball:"
        # return response
        return response


    def get_nfl_scoreboard_response(self):
        """Get NFL scoreboard response"""
        # set nfl scoreboard response
        response = "Sorry, it seems the NFL is not in season. :football:"
        # return response
        return response


    def can_process(self, statement):
        """Check statement if it should processed"""
        # initialize nltk stemmer
        ps = PorterStemmer()
        # get set of english stopwords
        stop_words = set(stopwords.words("english"))
        # cast statement to string
        statement = str(statement)

        # iterate through statement and split by logical words and make lowercase
        words = [x.lower() for x in word_tokenize(statement)]
        # remove required bot mention
        words = words[4::]

        # create statement list
        statement = []
        # iterate through words list
        for i in words:
            # check if word is not a stopword
            if i not in stop_words:
                #append to statement list the stemmed word that isn't a stop word
                statement.append(ps.stem(i))

        print(statement)

        # check for string in statement and return true to process and false to not process
        if "horse" in statement:
            return False
        elif "weather" in statement:
            return False
        elif "temperature" in statement:
            return False
        elif "cyride" in statement:
            return False
        elif "bus" in statement:
            return False
        elif "nba" in statement:
            if "scoreboard" in statement:
                return True
        elif "nhl" in statement:
            if "scoreboard" in statement:
                return True
        elif "mlb" in statement:
            if "scoreboard" in statement:
                return True
        elif "nfl" in statement:
            if "scoreboard" in statement:
                return True
        elif "schedul" in statement:
            if "hawk" in statement:
                return True
            elif "celtic" in statement:
                return True
            elif "net" in statement:
                return True
            elif "hornet" in statement:
                return True
            elif "bull" in statement:
                return True
            elif "cavalier" in statement:
                return True
            elif "maverick" in statement:
                return True
            elif "nugget" in statement:
                return True
            elif "piston" in statement:
                return True
            elif "warrior" in statement:
                return True
            elif "rocket" in statement:
                return True
            elif "pacer" in statement:
                return True
            elif "clipper" in statement:
                return True
            elif "laker" in statement:
                return True
            elif "grizzli" in statement:
                return True
            elif "heat" in statement:
                return True
            elif "buck" in statement:
                return True
            elif "timberwolv" in statement:
                return True
            elif "pelican" in statement:
                return True
            elif "knick" in statement:
                return True
            elif "thunder" in statement:
                return True
            elif "magic" in statement:
                return True
            elif "76er" in statement:
                return True
            elif "sun" in statement:
                return True
            elif "trail" and "blazer" in statement:
                return True
            elif "trailblaz" in statement:
                return True
            elif "king" in statement:
                return True
            elif "spur" in statement:
                return True
            elif "raptor" in statement:
                return True
            elif "jazz" in statement:
                return True
            elif "wizard" in statement:
                return True
            else:
                return False


    def process(self, statement):
        """If function can_process then this will work"""
        from chatterbot.conversation import Statement

        # set base confidence and bot_response
        confidence = 0
        bot_response = "Sorry, I couldn't find what you were looking for."

        # initialize nltk stemmer
        ps = PorterStemmer()
        # get set of english stopwords
        stop_words = set(stopwords.words("english"))
        # cast statement to string
        statement = str(statement)

        # iterate through statement and split by logical words and make lowercase
        words = [x.lower() for x in word_tokenize(statement)]
        # remove required bot mention
        words = words[4::]

        # create statement list
        statement = []
        # iterate through words list
        for i in words:
            # check if word is not a stopword
            if i not in stop_words:
                #append to statement list the stemmed word that isn't a stop word
                statement.append(ps.stem(i))

        # check for string in statement and if conditions are met
        # set bot response to appropriate response and set confidence to 1
        if "nba" in statement:
            if "scoreboard" in statement:
                bot_response = self.get_nba_scoreboard_response()
                confidence = 1
        elif "nhl" in statement:
            if "scoreboard" in statement:
                bot_response = self.get_nhl_scoreboard_response()
                confidence = 1
        elif "mlb" in statement:
            if "scoreboard" in statement:
                bot_response = self.get_mlb_scoreboard_response()
                confidence = 1
        elif "nfl" in statement:
            if "scoreboard" in statement:
                bot_response = self.get_nfl_scoreboard_response()
                confidence = 1
        elif "schedul" in statement:
            if "hawk" in statement:
                bot_response = self.get_nba_team_schedule("Hawks")
                confidence = 1
            elif "celtic" in statement:
                bot_response = self.get_nba_team_schedule("Celtics")
                confidence = 1
            elif "net" in statement:
                bot_response = self.get_nba_team_schedule("Nets")
                confidence = 1
            elif "hornet" in statement:
                bot_response = self.get_nba_team_schedule("Hornets")
                confidence = 1
            elif "bull" in statement:
                bot_response = self.get_nba_team_schedule("Bulls")
                confidence = 1
            elif "cavalier" in statement:
                bot_response = self.get_nba_team_schedule("Cavaliers")
                confidence = 1
            elif "maverick" in statement:
                bot_response = self.get_nba_team_schedule("Mavericks")
                confidence = 1
            elif "nugget" in statement:
                bot_response = self.get_nba_team_schedule("Nuggets")
                confidence = 1
            elif "piston" in statement:
                bot_response = self.get_nba_team_schedule("Pistons")
                confidence = 1
            elif "warrior" in statement:
                bot_response = self.get_nba_team_schedule("Warriors")
                confidence = 1
            elif "rocket" in statement:
                bot_response = self.get_nba_team_schedule("Rockets")
                confidence = 1
            elif "pacer" in statement:
                bot_response = self.get_nba_team_schedule("Pacers")
                confidence = 1
            elif "clipper" in statement:
                bot_response = self.get_nba_team_schedule("Clippers")
                confidence = 1
            elif "laker" in statement:
                bot_response = self.get_nba_team_schedule("Lakers")
                confidence = 1
            elif "grizzli" in statement:
                bot_response = self.get_nba_team_schedule("Grizzlies")
                confidence = 1
            elif "heat" in statement:
                bot_response = self.get_nba_team_schedule("Heat")
                confidence = 1
            elif "buck" in statement:
                bot_response = self.get_nba_team_schedule("Bucks")
                confidence = 1
            elif "timberwolv" in statement:
                bot_response = self.get_nba_team_schedule("Timberwolves")
                confidence = 1
            elif "pelican" in statement:
                bot_response = self.get_nba_team_schedule("Pelicans")
                confidence = 1
            elif "knick" in statement:
                bot_response = self.get_nba_team_schedule("Knicks")
                confidence = 1
            elif "thunder" in statement:
                bot_response = self.get_nba_team_schedule("Thunder")
                confidence = 1
            elif "magic" in statement:
                bot_response = self.get_nba_team_schedule("Magic")
                confidence = 1
            elif "76er" in statement:
                bot_response = self.get_nba_team_schedule("76ers")
                confidence = 1
            elif "sun" in statement:
                bot_response = self.get_nba_team_schedule("Suns")
                confidence = 1
            elif "trail" and "blazer" in statement:
                bot_response = self.get_nba_team_schedule("Trail Blazers")
                confidence = 1
            elif "trailblaz" in statement:
                bot_response = self.get_nba_team_schedule("Trail Blazers")
                confidence = 1
            elif "king" in statement:
                bot_response = self.get_nba_team_schedule("Kings")
                confidence = 1
            elif "spur" in statement:
                bot_response = self.get_nba_team_schedule("Spurs")
                confidence = 1
            elif "raptor" in statement:
                bot_response = self.get_nba_team_schedule("Raptors")
                confidence = 1
            elif "jazz" in statement:
                bot_response = self.get_nba_team_schedule("Jazz")
                confidence = 1
            elif "wizard" in statement:
                bot_response = self.get_nba_team_schedule("Wizards")
                confidence = 1

        # final response is cast to Statement and confidence is set to 0
        # (This tricks the machine learning to not confide in its own response)
        response_statement = Statement(bot_response)
        response_statement.confidence = confidence

        return response_statement

from chatterbot.logic import LogicAdapter
import base64
import requests
from pprint import pprint
import random
import re
import sys
import itertools


class horse_adapter(LogicAdapter):

    def __init__(self, **kwargs):
        super(horse_adapter, self).__init__(**kwargs)

    gameState = 0

    gamelist = []
    Right = []
    Wrong = []
    Guesses = []    # define arrays for config file to be read into
    gameWord = ""
    sBlank = ""

    matchedIndexes = []  # array for the indexes that match to be stored in

    def by_size(self, words, size):
        result = []
        for word in words:  # function that searches a list of words, and returns ones with matching length
            if len(word) == size:
                result.append(word)
        return result

    def ReloadConfig(self):
        global gamelist
        global Right
        global Wrong
        global Guesses
        global gameWord
        global MatchedIndexes

        gamelist = []
        Right = []
        Wrong = []
        Guesses = []
        MatchedIndexes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # stores the indexes of matches, length of array is longer than max length of word
        f = open("horse_data/CurGame.txt")
        for h in f.readlines():
            gamelist.append(h.strip().split('\t'))  # read in each file
        f = open("horse_data/Right.txt")          # put data into arrays
        for h in f.readlines():
            Right.append(h.strip().split('\t'))
        f = open("horse_data/Wrong.txt")
        for h in f.readlines():
            Wrong.append(h.strip().split('\t'))
        f = open("horse_data/Guesses.txt")
        for h in f.readlines():
            Guesses.append(h.strip().split('\t'))
        if(len(Wrong) >= 6):  # if wrong length is equal to length of horse, gamestate = 1 = loss
            self.gameState = 1

        gamelist = list(itertools.chain.from_iterable(gamelist))
        Guesses = list(itertools.chain.from_iterable(Guesses))
        Right = list(itertools.chain.from_iterable(Right))
        Wrong = list(itertools.chain.from_iterable(Wrong))  # flatten all arrays, otherwise they are lists of lists
        f.close()

        gameWord = gamelist[0].lower()  # grab the word being guessed at

        self.sBlank = gameWord  # sblank is used as the word with blanks over letters
        count = 0

        for i in range(0, len(Right)):

            for f in range(0, len(gameWord)):

                if(gameWord[f] == Right[i]):  # between length of right, and gameword, check each letter of Right against the gameWord
                    MatchedIndexes[f] = 1  # right contains only the correct guesses, logic for that is in Guess()
        for q in range(0, len(gameWord)):
            # print(MatchedIndexes[q])
            if(MatchedIndexes[q] == 0):     # matched indexes[0] indicates a not matched word
                self.sBlank = self.sBlank.replace(gameWord[q],"-")  # replace not matches with "-"
            else:
                count = count + 1

            if(count == len(gameWord)):
                                    # if the matched letters = the length of guessed at word, gamestate = 2 = win
                self.gameState = 2

    def Guess(self,ch):
        self.ReloadConfig()  # reload config called after in every function, ensures that data is up to date

        if(self.gameState == 0):    # if game is in session(state = 0)
            g = None # none is the case if letter does not match
            ch = ch.lower()  # lowercase everything
            self.ReloadConfig()  # check config again
            if(ch not in Guesses):  # if letter hasnt been guessed

                for i in range(0, len(gameWord)):

                    if(ch == gameWord[i]):  # if the letter is a match
                        f = open("horse_data/Right.txt", "a+")  # write letter into Right
                        f.write("\n" + ch)
                        f = open("horse_data/Guesses.txt", "a+")  # write letter into Guesses
                        f.write("\n" + ch)
                        g = 0
                        break  # end loop
                if(g == None):
                    f = open("horse_data/Wrong.txt", "a+")  # if not a match
                    f.write("\n" + ch)                    # write into Wrong, and Guesses.
                    f = open("horse_data/Guesses.txt", "a+") # Guesses is all guesses together
                    f.write("\n" + ch)

            self.ReloadConfig()
        else:
            print("Game over. No more guesses.")  # gamestate not in session

    def Init(self, length):  # init Function, handles starting a new game
        self.gameState = 0

        wordlist = []
        q = open("horse_data/Dictionary.txt")  # read in dictionary file
        for g in q.readlines():
            g = g.lower()
            wordlist.append(g.strip().split('\t'))  # split into words

        wordlist = list(itertools.chain.from_iterable(wordlist))  # flatten array

        if (length >= 1 and length <=14):  # checks against length value, could allow user to pass in length
            usedlist = self.by_size(wordlist, length)  # product doesnt end up using the length
            s = usedlist[(random.randrange(0, len(usedlist)))]  # get get a random word from the list

            f = open("horse_data/CurGame.txt", "w")
            # print("Truncating curGame")  # reset all text files
            f.truncate()
            f.write(s)
            f = open("horse_data/Guesses.txt", "w")
            f.truncate()
            f.write("GuessFile")
            f = open("horse_data/Right.txt", "w")
            f.truncate()
            f.write("CorrectGuesses")
            f = open("horse_data/Wrong.txt", "w")
            f.truncate()
            f.write("IncorrectGuesses")

        self.ReloadConfig()  # read in the new files

    def Check(self):  # check function returns the string of game status
        self.ReloadConfig()  # reload files
        g = ""
        if(len(Wrong) == 2):  # check length of wrong, for making the H O R S E text
            g += ("H\n")
        if(len(Wrong) == 3):
            g += ("H O\n")
        if(len(Wrong) == 4):
            g += ("H O R\n")
        if(len(Wrong) == 5):
            g += ("H O R S\n")
        if(len(Wrong) == 6):
            g += ("H O R S E\n")
        for f in range(0, len(self.sBlank)):  # put letters of sblank with spaces
            g += self.sBlank[f] + " "
        g += "\n"

        play_again_statements = []  # list of statements for the bot to say, more personable
        play_again_statements.append("Type *horse play* to play again!\n")
        play_again_statements.append("Want to play again? Type *horse play*.\n")
        play_again_statements.append("That was fun! Type *horse play* to play again!\n")
        if(self.gameState == 1):
            extra_statements = []
            extra_statements.append("\nYou have lost. The word was " + gameWord + ".\n")
            extra_statements.append("\nThe word was " + gameWord + ". Sorry!\n")
            extra_statements.append("\nMaybe you'll get it next time! The word was " + gameWord + ".\n")
            g += random.choice(extra_statements)
            g += random.choice(play_again_statements)
        elif(self.gameState == 2):
            extra_statements = []
            extra_statements.append("\nYou Have Won!\n")
            extra_statements.append("\nNice job!\n")
            extra_statements.append("\nWay to go! You're a pro!\n")
            g += random.choice(extra_statements)
            g += random.choice(play_again_statements)
        return g

    def can_process(self, statement):  # can process function reads in statement, returns true and goes to process, or false and doesnt
        statement = [x.lower() for x in statement.text.split()]
        statement = [re.sub(r'\W+', '', x) for x in statement]

        if "horse" in statement:
            return True
        else:
            return False

    def process(self, statement):  # process handles general read in logic
        from chatterbot.conversation import Statement

        confidence = 1
        bot_response = self.Check()  # default response is game status, as a check() call

        statement = [x.lower() for x in statement.text.split()]
        statement = [re.sub(r'\W+', '', x) for x in statement]

        if "horse" in statement:
            if "play" in statement:  # if user is attempting to start a game
                r = (random.randrange(2, 13))  # generate a number
                self.Init(r)  # start game with that length word
                bot_response = "I'm thinking of a word that's " + str(r) + " letters long.\n"
                bot_response += self.Check()  # add the game state to the string
                confidence = 1
            elif "guess" in statement:  # if user is guessing
                s = statement

                # print(s[3])
                self.Guess(s[3])  # guess the letter at index 3, which is the letter/string after guess
                bot_response = self.Check()  # update response with check()
        # print(str(bot_response))  # debug prints of what bot will say
        response_statement = Statement(str(bot_response))  # set response to the bot_response
        response_statement.confidence = 1
        # print(str(response_statement))
        return response_statement  # return this statement out.

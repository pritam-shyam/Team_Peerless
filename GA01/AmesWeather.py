from sys import argv
import weather.current
import weather.historical
from datetime import datetime, timedelta
from re import split
from time import time


startTime = time()
"""Run a command line prompt for interface"""
# Create the flags, and objects to be used later.
# Metric is the flag or metric conversion or not
metric = False
# Delta is the date time difference, if it exists
delta = None
# TimeOffset is the date to be used if we are using a different day for "today"
timeOffset = None
# isTimeOffset is used to check which functions to use
isTimeOffset = False
# Holds the 'flags' to switch functionality of the program.
flags = []
# arglist is the list of system arguements
arglist = [a.upper() for a in argv[1::]]
# badarg is for bad commands that arent in the program.
badarg = []
# funargs are functional args, used to check for bad args. Made a variable to increase readability.
funargs = ("T", "T-D", "T-W", "T-M", "T-Y", "P", "P-D", "P-W", "P-M", "P-Y", "WS", "WS-D", "WS-W", "WS-M", "WS-Y", "WD", "WD-D", "WD-W", "WD-M", "WD-Y")

# This splits arguements into badargs, flags, and arglist will be good commands.
# Need a place element to keep track of deletion of variables.
place = 0
while place < len(arglist):
    # If it is a -- command..
    if arglist[place].startswith("--"):
        # Put it into flags and delete from arglist
        flags.append(arglist[place])
        del arglist[place]
    # else if it is not a functioning arguement
    elif arglist[place] not in funargs:
        # add it to the badargs and delete it from the list
        badarg.append(arglist[place])
        del arglist[place]
    else:
        # Otherwise it is a good command, leave it in the list.
        place += 1


# Go through the flags and switch the correct boolean values
for i in range(len(flags)):
    arg = flags[i]
    if arg.startswith("--TIME-OFFSET"):
        # Split the command line arg up, and place in the datetime method.
        cmdtime = arg[arg.find("=") + 1::]
        t = split("[/ :]", cmdtime)
        try:
            # Put it into a date time
            timeOffset = datetime(int(t[2]), int(t[0]), int(t[1]), int(t[3]), int(t[4]))
        except:
            # If we get an error, we throw an error and exit.
            print("Day does not exist.")
            exit()
        # If all went well, flip the isTimeOffset to True
        isTimeOffset = True
    elif arg == "--METRIC":
        metric = True
    elif arg == "--HELP":
        file = open("help.txt", "r")
        print(file.read())
        exit()
    # Runs the GUI version
    elif arg == "--GUI":
        with open("gui.py") as sourceFile:
            exec(sourceFile.read())

# If we didnt have a timeoffset, we use today's time.
if timeOffset is None:
    timeOffset = datetime.now()

# For all te arguements in the list, we will find the correct function and print the result.
for i in range(len(arglist)):
        arg = arglist[i]
        # Find the correct command
        if arg.startswith("T"):
            # Then find the correct version of the command
            if arg == "T":
                # For the 'TODAY' functions, we need to see if today is offset.
                if isTimeOffset:
                    if metric:
                        # If it is metric, we print it with the conversion
                        print(weather.historical.getTemperature("C", tme=int((timeOffset).timestamp())), end="")
                    else:
                        # Otherwise pull it straight from the data.
                        print(weather.historical.getTemperature("F", tme=int((timeOffset).timestamp())), end="")
                else:
                    # If not, we can just get the current temp
                    print(weather.current.getTemperature(metric), end="")
            elif arg == "T-D":
                # delta is 1 day for '1 day ago'
                delta = timedelta(days=1)
                if metric:
                    print(weather.historical.getTemperature("C", tme=int((timeOffset - delta).timestamp())), end="")
                else:
                    print(weather.historical.getTemperature("F", tme=int((timeOffset - delta).timestamp())), end="")
            elif arg == "T-W":
                # delta is 7 day for '7 days ago'
                delta = timedelta(days=7)
                if metric:
                    print(weather.historical.getTemperature("C", tme=int((timeOffset - delta).timestamp())), end="")
                else:
                    print(weather.historical.getTemperature("F", tme=int((timeOffset - delta).timestamp())), end="")
            elif arg == "T-M":
                # delta is 28 day for '28 days ago' in compliance with constraints.
                delta = timedelta(days=28)
                if metric:
                    print(weather.historical.getTemperature("C", tme=int((timeOffset - delta).timestamp())), end="")
                else:
                    print(weather.historical.getTemperature("F", tme=int((timeOffset - delta).timestamp())), end="")
            elif arg == "T-Y":
                # Delta is 365.25 for 1 year ago, and compensates for leap year.
                delta = timedelta(days=365.25)
                if metric:
                    print(weather.historical.getTemperature("C", tme=int((timeOffset - delta).timestamp())), end="")
                else:
                    print(weather.historical.getTemperature("F", tme=int((timeOffset - delta).timestamp())), end="")
        elif arg.startswith("WS"):
            if arg == "WS":
                if isTimeOffset:
                    if metric:
                        print(weather.historical.getWindSpeed("KMH", tme=int(timeOffset.timestamp())), end="")
                    else:
                        print(weather.historical.getWindSpeed("MPH", tme=int(timeOffset.timestamp())), end="")
                else:
                    print(weather.current.getWindSpeed(metric), end="")
            elif arg == "WS-D":
                delta = timedelta(days=1)
                if metric:
                    print(weather.historical.getWindSpeed("KMH", tme=int((timeOffset - delta).timestamp())), end="")
                else:
                    print(weather.historical.getWindSpeed("MPH", tme=int((timeOffset - delta).timestamp())), end="")
            elif arg == "WS-W":
                delta = timedelta(days=7)
                if metric:
                    print(weather.historical.getWindSpeed("KMH", tme=int((timeOffset - delta).timestamp())), end="")
                else:
                    print(weather.historical.getWindSpeed("MPH", tme=int((timeOffset - delta).timestamp())), end="")
            elif arg == "WS-M":
                delta = timedelta(days=28)
                if metric:
                    print(weather.historical.getWindSpeed("KMH", tme=int((timeOffset - delta).timestamp())), end="")
                else:
                    print(weather.historical.getWindSpeed("MPH", tme=int((timeOffset - delta).timestamp())), end="")
            elif arg == "WS-Y":
                delta = timedelta(days=365.25)
                if metric:
                    print(weather.historical.getWindSpeed("KMH", tme=int((timeOffset - delta).timestamp())), end="")
                else:
                    print(weather.historical.getWindSpeed("MPH", tme=int((timeOffset - delta).timestamp())), end="")
        elif arg.startswith("P"):
            if arg == "P":
                if isTimeOffset:
                    if metric:
                        print(weather.historical.getPressure("mbar", tme=int(timeOffset.timestamp())), end="")
                    else:
                        print(weather.historical.getPressure("inHg", tme=int(timeOffset.timestamp())), end="")
                else:
                    print(weather.current.getPressure(metric), end="")
            elif arg == "P-D":
                delta = timedelta(days=1)
                if metric:
                    print(weather.historical.getPressure("mbar", tme=int((timeOffset - delta).timestamp())), end="")
                else:
                    print(weather.historical.getPressure("inHg", tme=int((timeOffset - delta).timestamp())), end="")
            elif arg == "P-W":
                delta = timedelta(days=7)
                if metric:
                    print(weather.historical.getPressure("mbar", tme=int((timeOffset - delta).timestamp())), end="")
                else:
                    print(weather.historical.getPressure("inHg", tme=int((timeOffset - delta).timestamp())), end="")
            elif arg == "P-M":
                delta = timedelta(days=28)
                if metric:
                    print(weather.historical.getPressure("mbar", tme=int((timeOffset - delta).timestamp())), end="")
                else:
                    print(weather.historical.getPressure("inHg", tme=int((timeOffset - delta).timestamp())), end="")
            elif arg == "P-Y":
                delta = timedelta(days=365.25)
                if metric:
                    print(weather.historical.getPressure("mbar", tme=int((timeOffset - delta).timestamp())), end="")
                else:
                    print(weather.historical.getPressure("inHg", tme=int((timeOffset - delta).timestamp())), end="")
        elif arg.startswith("WD"):
            if arg == "WD":
                if isTimeOffset:
                    print(weather.historical.getWindDirection(tme=int(timeOffset.timestamp())), end="")
                else:
                    print(weather.current.getWindDirection(), end="")
            elif arg == "WD-D":
                delta = timedelta(days=1)
                print(weather.historical.getWindDirection(tme=int((timeOffset - delta).timestamp())), end="")
            elif arg == "WD-W":
                delta = timedelta(days=7)
                print(weather.historical.getWindDirection(tme=int((timeOffset - delta).timestamp())), end="")
            elif arg == "WD-M":
                delta = timedelta(days=28)
                print(weather.historical.getWindDirection(tme=int((timeOffset - delta).timestamp())), end="")
            elif arg == "WD-Y":
                delta = timedelta(days=365.25)
                print(weather.historical.getWindDirection(tme=int((timeOffset - delta).timestamp())), end="")

        # This is for printing the commas in the command line.
        # If we still have arguements left, and it is not a flag, and it is not in the bad commands..
        if i != (len(arglist) - 1) and arg not in ["--METRIC", "--TIME-OFFSET"] and arg not in badarg:
            # We print a comma
            print(", ", end="")

print("")

# If the length of the bad arguements is zero, we dont need to print the bad arguements
if len(badarg) != 0:
    # Otherwise, we alert them of the bad commands!
    print("\nThe following commands are invalid: ", ", ".join(badarg),
          "\nPlease refer to the instructions manual or use --help.")

# used to print time taken to run program
# print("--- %s seconds ---" % (time() - startTime))

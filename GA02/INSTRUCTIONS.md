# User Manual

## Overview
TEAM-PEERLESS was tasked to create a chat bot that can be integrated into the Slack communication platform. A chat bot is a program that simulates a conversation with human users. These have many practical uses, such as answering questions, retrieving data, scheduling tasks or reminders, intelligent responses to basic conversational inputs, and can even include easter eggs to amuse the users.

The chat bot is a useful tool because it can replace several apps on the user's mobile device. For example, this chat bot accepts a Cy-Ride bus terminal or stop number and responds with the estimated time of arrival for any Cy-Ride buses that will arrive in the next 15 minutes. This weather information when requested by the user. Information includes temperature, wind speed, and wind directions.

The chat bot also has a professional sport information component that retrieves information on current sports games.

### How to Run the Program

To operate Cy-Bot, run the Cy-Bot-peerless.py in the Program folder.

Cy-Bot has the following features:

- *Weather*: Ask Cy-Bot what the weather is like. it will tell you the wind speed, and temperature, what if feels like outside.
- *Cyride*: Provide Cy-Bot with a bus top ID, and it can tell the busses arriving in the next 15 minutes
- *HORSE*: Say 'horse play' to begin a game, and 'horse guess X' to guess a letter!
- *Sports*: Provide Cy-Bot with 'nba/nhl/mlb/nfl scoreboard' and it can tell you the games today, and if they are in progress it can tell you the score.
  - It can also show you the game schedule for your favorite team. say '<nba_team_here> schedule' to take a peek!

There are also some hidden features. Try and talk with Cy-Bot and see what you can find!


### Components

Below are listed the tools we used to complete this project:

##### Dark Sky API
Allows you to request weather forecasts and historical weather data programmatically. It is the easiest, most advanced weather API on the web.

https://darksky.net/dev/

##### MySportsFeeds API
Consistent data for NFL, MLB, NBA, and NHL including Scoreboard, Boxscores, Schedules, Standings, Injuries and. The use of this API is free for educational purposes.

https://www.mysportsfeeds.com/

##### NextBus XML Feed API
Provides a Feed of the prediction and configuration information such that developers can create applications for providing passenger information to the public.

https://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf

##### Slack Client
Brings all your communication together in one place. It's real-time messaging, archiving and search for modern teams.

https://slack.com/

##### Atom
The code was written using Atom text editor.

https://atom.io/

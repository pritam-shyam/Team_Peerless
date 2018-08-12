from flask import Flask, redirect, url_for, request, render_template,session,flash
import hashlib
import binascii
import sqlite3
import os
from modules import DBTools
from modules import Trades
from modules import StockPrices
from modules import ad_factory
import json

import plotly.graph_objs as go
import plotly
import datetime
import pandas_datareader.data as web
from datetime import datetime

DBTools.initializeERD()

app = Flask(__name__)

WEB_APP_NAME = "Stock Market Simulation"


def grabStockGraph(StockName):
    df = web.DataReader(StockName, 'google', datetime(datetime.now().year - 1, datetime.now().month, datetime.now().day), datetime(datetime.now().year, datetime.now().month, datetime.now().day))
    trace = go.Candlestick(x=df.index,
                           open=df.Open,
                           high=df.High,
                           low=df.Low,
                           close=df.Close)
    data = [trace]
    plotly.offline.plot(data, filename='./static/stockplots/' + StockName + ".html", auto_open=False)


def getDashboardData():
    stocks = ['AAPL', 'GOOG', 'TSLA', 'XOM', 'AMZN']
    data = []
    for x in stocks:
        data.append(StockPrices.getAllDataList(x))
    return data

@app.route('/dashboard')
def dashboard():
    if session.get('logged_in'):
        with sqlite3.connect('mainDB.db') as conn:
            cash = DBTools.getUserCash(conn, userID=str(session['UserName']).lower())
            cash = '${:20,.2f}'.format(cash)
            netvalue = DBTools.getNetWorth(conn=conn, userID=str(session['UserName']).lower())
            netvalue = '${:20,.2f}'.format(netvalue)
        data = getDashboardData()
        return render_template("dashboard.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks(), data=data, UserCash=cash, NetValue=netvalue)
    else:
        return render_template("login.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks())


# Dont touch this.. It may stop working.
@app.route('/leaderboard')
def leaderboard():
    with sqlite3.connect('mainDB.db') as conn:
        data = DBTools.getUserRanks(conn)
        length = len(data) + 1
        data = json.dumps(data)
    if session.get('logged_in'):
        cash = DBTools.getUserCash(conn, userID=str(session['UserName']).lower())
        cash = '${:20,.2f}'.format(cash)
        return render_template("leaderboard.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks(), data=data, length=length, UserCash=cash)
    else:
        return render_template("leaderboard.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks(), data=data, length=length)


@app.route('/about')
def about():
    if session.get('logged_in'):
        with sqlite3.connect('mainDB.db') as conn:
            cash = DBTools.getUserCash(conn, userID=str(session['UserName']).lower())
            cash = '${:20,.2f}'.format(cash)
        return render_template("about.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks(), UserCash=cash)
    else:
        return render_template("about.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks())


@app.route('/contact')
def contact():
    if session.get('logged_in'):
        with sqlite3.connect('mainDB.db') as conn:
            cash = DBTools.getUserCash(conn, userID=str(session['UserName']).lower())
            cash = '${:20,.2f}'.format(cash)
        return render_template("contact.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks(), UserCash=cash)
    else:
        return render_template("contact.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks())


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return home()


@app.route('/login',methods=['POST'])
def do_admin_login():
    if request.form['signup'] == "login":
        conn = sqlite3.connect('mainDB.db')
        #conn = sqlite3.connect('mainDB.db')
        User = request.form['username']
        Pass = request.form['password']
        #file = open('testfile.txt','w')
        if not User:
            User = "None"
        User = User.lower()
        cur = conn.cursor()

        cur.execute("SELECT * from User where userID = ?;",(User,))
        rows = cur.fetchall();
        if(len(rows) > 0):
            #file.write(str(User))
            cur.execute("SELECT salt,password from User where userID = ?;",(User,))
            rows = cur.fetchall();
            Salt = rows[0][0]
            Password = rows[0][1]

            BSalt = Salt.encode('UTF-8')
            BPassword = Pass.encode('UTF-8')
            dk = hashlib.pbkdf2_hmac('sha256',BPassword,BSalt,100000)
            g = binascii.hexlify(dk).decode()
            #file.write(str(Salt))
            #file.write(str(Password))
            if(g == Password):
                session['logged_in'] = True
                session['UserName'] = User
            else:
                print("BadLogin")

            conn.close()

    elif request.form['signup'] == "SignUp":
        return render_template("signup.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks())

    return home()


@app.route('/signup', methods=['POST'])
def signup():
    NewName1 = request.form['firstname']
    NewName2 = request.form['lastname']
    NewUser = request.form['newUser']
    NewEmail = request.form['useremail']
    NewPass = request.form['PASSword2']
    conn = sqlite3.connect('mainDB.db')
    DBTools.addUser(conn, NewUser, NewEmail, NewPass, NewName1, NewName2, cash=10000.00, usertype='Standard', groupID=None)

    if not session.get('logged_in'):
        return render_template('login.html', ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks())

    return render_template("signup.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks())


@app.route('/portfolio')
def portfolio():
    if session.get('logged_in'):
        with sqlite3.connect('mainDB.db') as conn:
            userID = session['UserName']
            userID = str(userID).lower()
            data = DBTools.getOwnedStocksByID(conn, userID)
            length = len(data) + 1
            data = json.dumps(data)
            cash = DBTools.getUserCash(conn, userID=str(userID))
            cash = '${:20,.2f}'.format(cash)
            data2 = DBTools.getOwnedStocksByIDPrices(conn, userID=userID)
            length2 = len(data2) + 1
            data2 = json.dumps(data2)
            portfolioValue = DBTools.getPortfolioValue(conn, DBTools.getAllPortData(conn, userID=userID)[0]['portfolioID'])
            portfolioValue = '${:20,.2f}'.format(portfolioValue)

        return render_template("portfolio.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks(), data=data, length=length, UserCash=cash, length2=length2, prices=data2, portValue=portfolioValue)
    else:
        return render_template("login.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks())


@app.route('/help')
def help():
    if session.get('logged_in'):
        with sqlite3.connect('mainDB.db') as conn:
            cash = DBTools.getUserCash(conn, userID=str(session['UserName']).lower())
            cash = '${:20,.2f}'.format(cash)
        return render_template("help.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks(), UserCash=cash)
    else:
        return render_template("help.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks())


@app.route('/stock/post',methods=['POST'])
def PostStock():
    with sqlite3.connect('mainDB.db') as conn:
        Action = request.form['Action']
        Quantity = request.form['Quantity']
        Ticker = request.form['Ticker']

        TickerPath = Ticker + ".html"
        data = StockPrices.getAllStockData(Ticker)
        sUrl = url_for('static', filename='./stockplots/' + TickerPath)
        User = session['UserName']

        # file = open('testfile.txt','w')
        # file.write(str(User))
        # file.close()
        User2 = str(User)
        Price = StockPrices.getPrice(Ticker)
        Price = float(Price)
        Quantity = float(Quantity)
        total = (Price * Quantity)
        total = '${:20,.2f}'.format(total)
        port = DBTools.getAllPortData(conn, User2)[0]['portfolioID']

        if(Action == 'Buy'):
            if(Trades.buyStock(conn, Ticker, port, Price, Quantity)):
                flash("Purchased " + str(Quantity) + " Stock from " + str(Ticker) + " for " + str(total))
            else:
                flash("Could not Complete Purchase")
        elif(Action == 'Sell'):
            if(Trades.sellStock(conn, Ticker, port, Price, Quantity)):
                flash("Sold " + str(Quantity) + " Stock from " + str(Ticker) + " for " + str(total))
            else:
                flash("Could not Sell Stock")
        Quant = DBTools.getPortfolioStocks(conn, str(session['UserName']).lower(), Ticker)
        cash = DBTools.getUserCash(conn, userID=str(session['UserName']).lower())
        cash = '${:20,.2f}'.format(cash)
        return render_template("stock.html", ad=ad_factory.get_ad(1), availableStocks=DBTools.getAvailableStocks(), ticker=Ticker, sUrl=sUrl, stock_data=data, ownedQuantity=Quant, UserCash=cash)

@app.route('/stock/<ticker>')
def stock_profile(ticker):

    tickerpath = ticker + ".html"
    grabStockGraph(ticker)
    # Action = request.form['Action']
    # Quantity = request.form['Quantity']
    data = StockPrices.getAllStockData(ticker)
    # print(data)

    sUrl = url_for('static', filename='./stockplots/' + tickerpath)


    if session.get('logged_in'):
        with sqlite3.connect('mainDB.db') as conn:
            Quant = DBTools.getPortfolioStocks(conn, str(session['UserName']).lower(), ticker)
            cash = DBTools.getUserCash(conn, userID=str(session['UserName']).lower())
            cash = '${:20,.2f}'.format(cash)
        return render_template("stock.html", ad=ad_factory.get_ad(1), availableStocks=DBTools.getAvailableStocks(), ticker=ticker, sUrl=sUrl, stock_data=data, ownedQuantity=Quant, UserCash=cash)
    else:
        return render_template("login.html", ad=ad_factory.get_ad(1), availableStocks=DBTools.getAvailableStocks())

@app.route('/premium')
def premium():
    if session.get('logged_in'):
        with sqlite3.connect('mainDB.db') as conn:
            cash = DBTools.getUserCash(conn, userID=str(session['UserName']).lower())
            cash = '${:20,.2f}'.format(cash)
            return render_template("premium.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks(), UserCash=cash)
    else:
        return render_template("premium.html", ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks(), UserCash=cash)

@app.route('/')
def home(name=WEB_APP_NAME, lb_data=getDashboardData()):
    if not session.get('logged_in'):
        return render_template('login.html', ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks())
    else:
        with sqlite3.connect('mainDB.db') as conn:
            cash = DBTools.getUserCash(conn, userID=str(session['UserName']).lower())
            cash = '${:20,.2f}'.format(cash)
            netvalue = DBTools.getNetWorth(conn=conn, userID=str(session['UserName']).lower())
            netvalue = '${:20,.2f}'.format(netvalue)
        return render_template("dashboard.html", data=lb_data, ad=ad_factory.get_ad(), availableStocks=DBTools.getAvailableStocks(), UserCash=cash, NetValue=netvalue)

@app.context_processor
def utility_processor():
  def iterateStocks():
    availableStocks = DBTools.getAvailableStocks()
    return availableStocks
  return dict(availableStocks=iterateStocks)

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host="0.0.0.0", port=8080, debug=True)

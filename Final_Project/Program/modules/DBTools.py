import sqlite3
import csv
import datetime
import time
from . import StockPrices
import hashlib
import binascii
import bcrypt

# Factory turns result sets into dictionary
# http://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
# This makes it easier to access info in later methods.
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# Create the DB
def initializeERD():
    '''Function to create the DB'''
    conn = sqlite3.connect('mainDB.db')
    print("Opened database successfully")

    # Create tables
    conn.execute('CREATE TABLE IF NOT EXISTS Stock (Ticker text, name text, PRIMARY KEY(ticker));')
    conn.execute('CREATE TABLE IF NOT EXISTS User (userID text, email text, groupID text, password text, first text, last text, cash real, usertype text, salt text, PRIMARY KEY(userID));')
    conn.execute('CREATE TABLE IF NOT EXISTS Portfolio (portfolioID text PRIMARY KEY, portfolioname text, portfolioType text, userID REFERENCES user(userID));')
    conn.execute('CREATE TABLE IF NOT EXISTS PortTransaction (DateOfTransaction text, type text NOT NULL CHECK (type IN ("buy", "Buy", "Sell", "sell", "Trade", "trade")), price real, quantity integer, portfolioID REFERENCES portfolio(portfolioID), ticker REFERENCES Stock(ticker), PRIMARY KEY(DateOfTransaction, portfolioID, ticker));')
    conn.execute('CREATE TABLE IF NOT EXISTS Standard (userID text PRIMARY KEY REFERENCES user(userID));')
    conn.execute('CREATE TABLE IF NOT EXISTS Premium (userID text PRIMARY KEY REFERENCES user(userID)); ')
    conn.execute('CREATE TABLE IF NOT EXISTS Offering (offerID text PRIMARY KEY, offerPrice real, description text);')
    conn.execute('CREATE TABLE IF NOT EXISTS UserTransaction (TransactionID integer PRIMARY KEY, transactionAmount real, paymentType text, userID REFERENCES user(userID));')
    conn.execute('CREATE TABLE IF NOT EXISTS OrderLine (TransactionID integer REFERENCES UserTransaction(TransactionID), offerID text REFERENCES Offering(offerID), orderDate text, PRIMARY KEY(TransactionID, offerID, orderDate));')
    print('Created tables Succefully')
    cur = conn.cursor()
    # Make sure we dont have the stock data in there
    cur.execute('SELECT COUNT(*) FROM Stock')
    if cur.fetchone()[0] is 0:
        # if we dont, we import it.
        importStocks('modules\\files\\TickersAndNames.csv', conn=conn)
        print('Imported Stock Data successfully')
    # otherwise dont
    else:
        print('stock data already present, did not import.')
    conn.close()



def importStocks(filename, conn):
    '''Import stocks into the DB, given a file name. '''
    with open(filename, newline="") as tickers:
        reader = csv.reader(tickers)
        # create a list to add into the DB
        to_db = [(line[0], line[1]) for line in reader]
        cur = conn.cursor()
        # add it in!
        cur.executemany('INSERT INTO Stock VALUES (?,  ?);', to_db)
        conn.commit()
        # print('success')
        cur.close()


# Returns all stocks in the DB.
def getAvailableStocks():
    '''Return all stocks'''
    with sqlite3.connect('mainDB.db') as conn:
        conn.row_factory = None
        cur = conn.cursor()
        cur.execute('SELECT * FROM Stock')
        return cur.fetchall()


def checkDuplicateUser(conn, userID):
    '''Check for duplicate user in the DB.'''
    conn.row_factory = None
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM user WHERE userID = ?', [userID.lower()])
    thing = cur.fetchone()
    # if the result set is greater than zero
    if thing[0] > 0:
        cur.close()
        # a user existss
        return True
    else:
        cur.close()
        # it doesnt exist.
        return False


def addUser(conn, userID, email, password, first, last, cash=10000.00, usertype='Standard', groupID=None):
    '''Add a user into the DB.'''
    cur = conn.cursor()
    # if it is not a duplicate user.. try and add the user. Return True
    # print(checkDuplicateUser(conn, userID))
    if not checkDuplicateUser(conn, userID):
        try:
            # Salting the password field.
            salt = bcrypt.gensalt()
            s = salt.decode()
            BSalt = s.encode('UTF-8')
            BPassword = password.encode('UTF-8')
            dk = hashlib.pbkdf2_hmac('sha256',BPassword,BSalt,100000)
            p = binascii.hexlify(dk).decode()
            # Insert it
            cur.execute('INSERT INTO user (userID, email, password, first, last, cash, usertype, groupID, salt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', [userID.lower(), email, p, first, last, cash, usertype, groupID, s])
            conn.commit()
            cur.close()
            # Now we add a portfolio for the user.
            nextNo = getNextPortID(conn)
            addPortData(conn=conn, userID=userID, portfolioID=nextNo, portfolioname=userID, portfolioType='Stock')

            return True
        except:
            return False
    else:
        return False


# Get all the data, with the dict_factory.
# This is used to make the code a bit more readable and easy to use.
def getAllUserData(conn, userID):
    '''Retreive all user data'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT * FROM user WHERE userID = ?', [userID.lower()])
    return cur.fetchone()


def getUserFullName(conn, userID):
    '''Get user full name'''
    data = getAllUserData(conn, userID)
    first, last = data['first'], data['last']
    return (first, last)


def getUserRanks(conn):
    '''Get user ranks. used for leaderboard'''
    conn.row_factory = None
    cur = conn.cursor()
    cur.execute('SELECT userID, cash FROM user ORDER BY cash DESC LIMIT 20;')
    startData = cur.fetchall()
    # data = [x, '{:20,.2f}'.format(y[1]) for x,y in data]
    data = []
    if(len(startData) is not 0):
        for x in startData:
            data.append([x[0].title(), '${:20,.2f}'.format(x[1])])

    return data


def getUserFirstName(conn, userID):
    '''Get user first name'''
    data = getAllUserData(conn, userID)
    first = data['first']
    return first


def getUserLastName(conn, userID):
    '''Get user last name'''
    data = getAllUserData(conn, userID)
    first = data['last']
    return first


def getUserCash(conn, userID):
    '''Get user current cash.'''
    data = getAllUserData(conn, userID)
    cash = data['cash']
    return round(float(cash), 2)


def getUserEMail(conn, userID):
    '''Get user email'''
    data = getAllUserData(conn, userID)
    email = data['email']
    return email


def getUserType(conn, userID):
    '''Get user type. checks premium or not.'''
    data = getAllUserData(conn, userID)
    type = data['usertype']
    return type


def getUserGroupID(conn, userID):
    '''Get user group if they have any'''
    data = getAllUserData(conn, userID)
    groupID = data['groupID']
    return groupID


def setUserFirstName(conn, userID, newfirst):
    '''Set user first name'''
    cur = conn.cursor()
    try:
        cur.execute('UPDATE user SET first = ? WHERE userID = ?', [newfirst, userID.lower()])
        cur.close()
        return True
    except:
        cur.close()
        return False


def setUserLastName(conn, userID, newlast):
    '''Set user last name'''
    cur = conn.cursor()
    try:
        cur.execute('UPDATE user SET last = ? WHERE userID = ?', [newlast, userID.lower()])
        cur.close()
        return True
    except:
        cur.close()
        return False


def setUserCash(conn, userID, cash):
    '''Set user cash. Testing only'''
    cur = conn.cursor()
    try:
        cur.execute('UPDATE user SET cash = ? WHERE userID = ?', [cash, userID.lower()])
        cur.close()
        return True
    except:
        cur.close()
        return False


def setUserEMail(conn, userID, newemail):
    '''Set user email.'''
    cur = conn.cursor()
    try:
        cur.execute('UPDATE user SET email = ? WHERE userID = ?', [newemail, userID.lower()])
        cur.close()
        return True
    except:
        cur.close()
        return False


def setUserType(conn, userID, newUserType):
    '''Set user type. change from premium to free, or free to premium.'''
    cur = conn.cursor()
    try:
        cur.execute('UPDATE user SET usertype = ? WHERE userID = ?', [newUserType, userID.lower()])
        cur.close()
        return True
    except:
        cur.close()
        return False


def setUserGroupID(conn, userID, newGroupID):
    '''Set user group ID'''
    cur = conn.cursor()
    try:
        cur.execute('UPDATE user SET groupID = ? WHERE userID = ?', [newGroupID, userID.lower()])
        cur.close()
        return True
    except:
        cur.close()
        return False


def getAllStockData(conn, ticker):
    '''given a stock ticker, get the name for i.t'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT * FROM stock WHERE ticker = ?', [ticker.upper()])
    return cur.fetchone()


def getStockCompanyName(conn, ticker):
    '''Get the company name for the ticker.'''
    data = getAllStockData(conn, ticker)
    return data['name']


def getNextPortID(conn):
    '''Retreive the next available portID'''
    conn.row_factory = None
    cur = conn.cursor()
    cur.execute('SELECT max(portfolioID) FROM Portfolio')
    data = cur.fetchall()
    if len(data) == 0:
        return(str(0))
    else:
        return str(int(data[0][0]) + 1)


def addPortData(conn, portfolioID, portfolioname, userID, portfolioType='Stock'):
    '''Add a portfolio to a user'''
    cur = conn.cursor()
    # if it is not a duplicate user.. try and add the user. Return True
    try:
        cur.execute('INSERT INTO Portfolio (portfolioID, portfolioname, portfolioType, userID) VALUES (?, ?, ?, ?);', [portfolioID, portfolioname, portfolioType, userID.lower()])
        conn.commit()
        cur.close()
        return True
    except:
        return False


def getAllPortData(conn, userID):
    '''get portfolios of a given user'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT * FROM Portfolio WHERE userID = ?', [userID.lower()])
    return cur.fetchall()


def getPortfolioNames(conn, userID):
    '''get names of a user's portfolios'''
    data = getAllPortData(conn, userID)
    return [(port['portfolioID'], port['portfolioname']) for port in data]


def getPortfolioTypes(conn, userID):
    '''get types of a user's portfolios'''
    data = getAllPortData(conn, userID)
    return [(port['portfolioID'], port['portfolioType']) for port in data]


def getPortfolioOwner(conn, portfolioID):
    '''get owner given a portfolioID'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    # if it is not a duplicate user.. try and add the user. Return True
    try:
        cur.execute('SELECT userID FROM Portfolio WHERE portfolioID = ?;', [portfolioID])
        conn.commit()
        owner = cur.fetchone()['userID']
        cur.close()
        return owner
    except:
        return False


def getAllPortTransactionData(conn, portfolioID, ticker):
    '''get all portfolio transaction data from a portfolio, and ticker. '''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT * FROM PortTransaction WHERE portfolioID = ? AND ticker = ?', [portfolioID, ticker.upper()])
    return cur.fetchall()


# YYYY-MM-DD HH:MM:SS
# DateOfTransaction, type, price, quantity, portfolioID, ticker
def addPortTransaction(conn, price, quantity, portfolioID, ticker, type='Buy'):
    '''Add a portfolio transaction'''
    cur = conn.cursor()
    # These set the quantities to the correct things for buy or sell.
    # Helps later whene valuating the value of portfolios
    if type.lower() == 'buy':
        quantity = abs(quantity)
    elif type.lower() == 'sell':
        quantity = abs(quantity) * -1
    elif type.lower() == 'trade':
        quantity = abs(quantity) * -1
    try:
        cur.execute('INSERT INTO PortTransaction (DateOfTransaction, type, price, quantity, portfolioID, ticker) VALUES (?, ?, ?, ?, ?, ?);', [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f'), type.lower(), price, quantity, portfolioID, ticker])
        conn.commit()
        cur.close()
        return True
    except:
        return False


def addOffering(conn, offerID, offerPrice, description):
    '''Add an offer to the DB.'''
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO Offering (offerID, offerPrice, description) VALUES (?, ?, ?);', [offerID, offerPrice, description])
        conn.commit()
        cur.close()
        return True
    except:
        return False


def getOneOfferingData(conn, OfferID):
    '''Get a specific offer's data'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT * FROM Offering WHERE offerID = ?', [OfferID])
    return cur.fetchone()


def getAllOfferingData(conn):
    '''Show all offers.'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT * FROM Offering')
    return cur.fetchall()


def addUserTransaction(conn, TransactionID, transactionAmount, paymentType, userID):
    '''Add a transaction for the offerings. '''
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO UserTransaction (TransactionID, transactionAmount, paymentType, userID) VALUES (?, ?, ?, ?);', [TransactionID, transactionAmount, paymentType, userID.lower()])
        conn.commit()
        cur.close()
        return True
    except:
        return False


def getOneUserTransactionData(conn, TransactionID):
    '''get a specific transaction ID'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT * FROM UserTransaction WHERE TransactionID = ?', [TransactionID])
    return cur.fetchone()


def getAllUserTransactionData(conn, userID):
    '''Get a user's entire transaction history'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT * FROM UserTransaction where userID = ?', [userID.lower()])
    return cur.fetchall()


def addOrderLine(conn, TransactionID, offerID):
    '''Add a transaction to the orderline.'''
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO OrderLine (TransactionID, offerID, orderDate) VALUES (?, ?, ?);', [TransactionID, offerID, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')])
        conn.commit()
        cur.close()
        return True
    except:
        return False


def getOrderLine(conn, TransactionID, offerID):
    '''Show the orderline'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT * FROM OrderLine WHERE TransactionID = ? AND offerID = ?', [TransactionID, offerID])
    return cur.fetchone()


def getPortfolioValue(conn, PortfolioID):
    conn.row_factory = dict_factory
    '''Get the amount of money tied up in a portfolio, given the market price.'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT ticker, sum(quantity) AS Net From PortTransaction WHERE PortfolioID = ? GROUP BY ticker HAVING type <> "Trade"', [PortfolioID])
    data = cur.fetchall()

    value = 0
    for row in data:
        value += int(row['Net']) * StockPrices.getPrice(row['ticker'])
    return round(value, 2)


def getNetWorth(conn, userID):
    '''Retreives the users networth, which is total portfolio and user cash.'''
    cash = getUserCash(conn, userID=userID)
    # Switch it back to NONE after get cash.
    conn.row_factory = None
    cur = conn.cursor()
    cur.execute('SELECT portfolioID FROM Portfolio WHERE userID = ?', [userID])
    data = cur.fetchall()
    newdata = []
    print(data)
    for x in data:
        for y in x:
            newdata.append(int(y))
            newdata.append(str(y))
    print(newdata)
    totalValue = cash
    for id in newdata:
        totalValue += getPortfolioValue(conn, id)
    return totalValue


# Get trades from a portfolio
def getAllTrades(conn, PortfolioID):
    '''Gets all trades present in a portfolio'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT * FROM PortTransaction WHERE portfolioID = ? AND type = "Trade"', [PortfolioID])
    # cur.execute('SELECT * FROM PortTransaction')
    return cur.fetchall()

# Use this to get all trades of a ticker.
def getAllTradesTicker(conn, ticker):
    '''Gets all trades present in for a ticker'''
    # This will be used in future releases
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT * FROM PortTransaction WHERE ticker = ? AND type = "Trade"', [ticker])
    # cur.execute('SELECT * FROM PortTransaction')
    return cur.fetchall()


# Use this to get all trades of a ticker.
def getSpecificTrade(conn, ticker, portfolioID, datetime):
    '''Gets the values for a specific trade.'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('SELECT * FROM PortTransaction WHERE ticker = ? AND portfolioID = ? AND DateOfTransaction = ? AND type = "Trade"', [ticker, portfolioID, datetime])
    # cur.execute('SELECT * FROM PortTransaction')
    return cur.fetchone()


def updateSpecificTrade(conn, ticker, portfolioID, datetime, type):
    '''Update the values for a specific trade, if needed.'''
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute('UPDATE PortTransaction SET type = ? WHERE ticker = ? AND portfolioID = ? AND DateOfTransaction = ?', [type, ticker, portfolioID, datetime])
    # cur.execute('SELECT * FROM PortTransaction')
    return cur.fetchone()


def getPortfolioStocks(conn, userID, ticker):
    '''Retreive the total amount of specifc stocks owned from all portfolios a user owns.'''
    conn.row_factory = None
    cur = conn.cursor()
    # Get the portfolio IDs
    cur.execute('SELECT portfolioID FROM Portfolio WHERE userID = ?', [userID])
    data = cur.fetchall()
    newdata = []
    # Because we are using this query in another, we need to make it in the right format.
    # Had an error here, need it to be just a tuple, not a list of tuples. Fixing below.
    for x in data:
        for y in x:
            # Did both string and int to make sure that our method does not miss any stocks.
            newdata.append(int(y))
            newdata.append(str(y))
    # Get the count
    cur.execute('SELECT SUM(quantity) FROM PortTransaction WHERE portfolioID IN ' + str(tuple(newdata)) + ' AND Ticker = ? AND type <> "Trade" GROUP BY Ticker;', [ticker])

    result = cur.fetchall()
    if len(result) == 0:
        return 0
    else:
        return(result[0][0])


def getOwnedStocksByID(conn, userID):
    '''Retreive the total amount of stocks owned from all portfolios a user owns.'''
    conn.row_factory = None
    cur = conn.cursor()
    cur.execute('SELECT portfolioID FROM Portfolio WHERE userID = ?', [userID])
    data = cur.fetchall()
    newdata = []
    for x in data:
        for y in x:
            newdata.append(int(y))
            newdata.append(str(y))
    cur.fetchall()

    # cur.execute('SELECT ticker, price, SUM(quantity) FROM PortTransaction WHERE portfolioID IN ' + str(tuple(newdata)) + ' AND type <> "Trade" GROUP BY Ticker, price HAVING SUM(quantity) > 0;')
    # Below works for quantity
    cur.execute('SELECT ticker, SUM(quantity) FROM PortTransaction WHERE portfolioID IN ' + str(tuple(newdata)) + ' AND type <> "Trade" GROUP BY Ticker HAVING SUM(quantity) > 0;')
    # cur.execute('SELECT ticker FROM PortTransaction WHERE portfolioID IN ' + str(tuple(newdata)) + ' AND type <> "Trade" GROUP BY Ticker HAVING SUM(quantity) > 0;')
    # innertable = cur.fetchall()
    # newinnertable = []
    # for x in innertable:
    #     for y in x:
    #         newinnertable.append(str(y))
    #
    # cur.execute('SELECT ticker, price FROM PortTransaction WHERE portfolioID IN ' + str(tuple(newdata)) + ' AND Ticker IN ' + str(tuple(newinnertable)) + ' AND type <> "Trade" GROUP BY Ticker, price HAVING SUM(quantity) > 0;')
    return cur.fetchall()


def getOwnedStocksByIDPrices(conn, userID):
    '''Retreive the total amount of stocks owned from all portfolios a user owns.'''
    conn.row_factory = None
    cur = conn.cursor()
    cur.execute('SELECT portfolioID FROM Portfolio WHERE userID = ?', [userID])
    data = cur.fetchall()
    newdata = []
    for x in data:
        for y in x:
            newdata.append(int(y))
            newdata.append(str(y))
    cur.fetchall()

    cur.execute('SELECT ticker FROM PortTransaction WHERE portfolioID IN ' + str(tuple(newdata)) + ' AND type <> "Trade" GROUP BY Ticker HAVING SUM(quantity) > 0;')
    innertable = cur.fetchall()
    newinnertable = []
    for x in innertable:
        for y in x:
            newinnertable.append(str(y))
    cur.fetchall()
    newdata = str(tuple(newdata))
    # print(newdata)
    # print(len(newinnertable))
    # print(newinnertable[0])
    # fix for 1 length tuples..
    if len(newinnertable) == 1:
        newinnertable = "(\'" + str(newinnertable[0]) + "\')"
    else:
        newinnertable = str(tuple(newinnertable))
    # print(newinnertable)

    cur.execute('SELECT ticker, price FROM PortTransaction WHERE portfolioID IN ' + newdata + ' AND ticker IN ' + newinnertable + ' AND type <> "Trade" GROUP BY Ticker, price HAVING SUM(quantity) > 0;')
    return cur.fetchall()

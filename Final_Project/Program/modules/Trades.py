from . import DBTools


# This is used for buying stock, unlimited amount from computers.
def buyStock(conn, ticker, portfolioID, marketPrice, quantity):
    '''Method to perfrom a stock buy'''
    # Get the owner
    owner = DBTools.getPortfolioOwner(conn, portfolioID)
    # current cash.
    currentCash = DBTools.getUserCash(conn, owner)
    # What is the total for the sale.
    saleTotal = (marketPrice * quantity)
    if(saleTotal < currentCash):
        # Add the stock to the data
        DBTools.addPortTransaction(conn, price=marketPrice, quantity=quantity, portfolioID=portfolioID, ticker=ticker, type='Buy')
        # Subtract cash
        newcash = currentCash - saleTotal
        DBTools.setUserCash(conn, userID=owner, cash=newcash)
        return True
    else:
        return False


# This is used for Selling stock, unlimited amount from computers.
def sellStock(conn, ticker, portfolioID, marketPrice, quantity):
    '''Method to perfrom a stock sale'''
    owner = DBTools.getPortfolioOwner(conn, portfolioID)
    currentCash = DBTools.getUserCash(conn, owner)
    saleTotal = (marketPrice * quantity)

    # quantity of stock that user owns.
    Quant = DBTools.getPortfolioStocks(conn, owner, ticker)
    # Add the stock to the data
    if(Quant >= quantity):
        DBTools.addPortTransaction(conn, price=marketPrice, quantity=quantity, portfolioID=portfolioID, ticker=ticker, type='Sell')
        # Add cash
        newcash = currentCash + saleTotal
        DBTools.setUserCash(conn, userID=owner, cash=newcash)
        return True
    else:
        return False


# Trades must be bought from user if not at market price.
def postTrade(conn, askingPrice, quantity, portfolioID, ticker):
    owner = DBTools.getPortfolioOwner(conn, portfolioID)
    return DBTools.addPortTransaction(conn, price=askingPrice, quantity=quantity, portfolioID=portfolioID, ticker=ticker, type='Trade')


# def updateTrade(conn, datetime, )

# Trades must be bought from user if not at market price.
def buyTrade(conn, tradedatetime, tradeportfolioID, ticker, buyerportfolioID):
    # update the trade to be a sell
    buyer = DBTools.getPortfolioOwner(conn, buyerportfolioID)
    seller = DBTools.getPortfolioOwner(conn, tradeportfolioID)
    buyerCash = DBTools.getUserCash(conn, buyer)
    sellerCash = DBTools.getUserCash(conn, seller)
    tradeData = DBTools.getSpecificTrade(conn, ticker=ticker, portfolioID=tradeportfolioID, datetime=tradedatetime)
    price = round(float(tradeData['price']), 2)
    quantity = abs(int(tradeData['quantity']))
    saleTotal = price * quantity

    if(saleTotal < buyerCash):
        # Update trade to be a sell
        DBTools.updateSpecificTrade(conn, ticker=ticker, datetime=tradedatetime, portfolioID=tradeportfolioID, type='Sell')
        # create the buy
        DBTools.addPortTransaction(conn, price=price, quantity=quantity, portfolioID=buyerportfolioID, ticker=ticker, type='Buy')
        # Subtract the cash from buyer
        buyerCash = buyerCash - saleTotal
        DBTools.setUserCash(conn, userID=buyer, cash=buyerCash)
        sellerCash = sellerCash + saleTotal
        DBTools.setUserCash(conn, userID=seller, cash=sellerCash)
        return True
    else:
        return(False)
        # TODO: ADD AN EXCEPTION HERE
    # update the trade to be a sell, and make the buy

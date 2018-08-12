import csv
import pprint
from yahoo_finance import Share
import random

def getAllData(ticker):
    stock = Share(ticker)
    data = {'name': stock.get_name(), 'price': stock.get_price(), 'open': stock.get_open(), 'prev_close': stock.get_prev_close()}
    return data


def getName(ticker):
    stock = Share(ticker)
    data = stock.get_name()
    return data


with open("ticker.csv", newline="") as file:
    # Create the reader
    reader = csv.reader(file)
    tickers = []
    for line in reader:
        tickers.append(line[0])

    # data = []
    # for x in random.sample(tickers, 10):
    #     data.append(getAllData(x))
    # for x in data:
    #     pprint.pprint(x)
    data = []

    for t in tickers:
        data.append([t, getName(t)])

    with open('TickersAndNames.csv', 'w', newline='') as csvfile:
        for x in data:
            Tickerwriter = csv.writer(csvfile, delimiter=',', dialect='excel')
            Tickerwriter.writerow([x[0], x[1]])

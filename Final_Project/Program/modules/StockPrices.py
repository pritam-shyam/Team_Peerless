from yahoo_finance import Share
import csv
import random


def getPrice(ticker):
    '''Get the price for the given ticker'''
    stock = Share(ticker)
    return float(stock.get_price())


def getName(ticker):
    '''Get the name of the company for the given ticker'''
    stock = Share(ticker)
    return stock.get_name()


def getAllData(ticker):
    '''Get the all data for the given ticker'''
    stock = Share(ticker)
    data = {'name': stock.get_name(), 'price': stock.get_price(), 'open': stock.get_open(), 'prev_close': stock.get_prev_close()}
    return data


def getAllDataList(ticker):
    '''Get the all data for the given ticker in a list'''
    stock = Share(ticker)
    data = [ticker, stock.get_name(), stock.get_price(), stock.get_open(), stock.get_prev_close()]
    return data


def getRandomTickers(size, filename):
    '''Get a few random tickers.'''
    with open(filename, newline="") as file:
        # Create the reader
        reader = csv.reader(file)
        tickers = []
        for line in reader:
            tickers.append(line[0])

        data = []
        for x in random.sample(tickers, size):
            data.append(getAllData(x))
        return data

def getAllStockData(ticker):
    '''Get a few random tickers.'''
    stock = Share(ticker)
    stock.refresh()
    data = {
        'name': stock.get_name(),
        'price': stock.get_price(),
        'change': stock.get_change(),
        'volume': stock.get_volume(),
        'prev_close': stock.get_prev_close(),
        'open': stock.get_open(),
        'avg_daily_volume': stock.get_avg_daily_volume(),
        'stock_exchange': stock.get_stock_exchange,
        'market_cap': stock.get_market_cap(),
        'book_value': stock.get_book_value(),
        'ebitda': stock.get_ebitda(),
        'dividend_share': stock.get_dividend_share(),
        'dividend_yield': stock.get_dividend_yield(),
        'earnings_share': stock.get_earnings_share(),
        'days_high': stock.get_days_high(),
        'days_low': stock.get_days_low(),
        'year_high': stock.get_year_high(),
        'year_low': stock.get_year_low(),
        '50day_moving_avg': stock.get_50day_moving_avg(),
        '200day_moving_avg': stock.get_200day_moving_avg(),
        'price_earnings_ratio': stock.get_price_earnings_ratio(),
        'price_earnings_growth_ratio': stock.get_price_earnings_growth_ratio(),
        'get_price_sales': stock.get_price_sales(),
        'get_price_book': stock.get_price_book(),
        'get_short_ratio': stock.get_short_ratio(),
        'trade_datetime': stock.get_trade_datetime(),
        'percent_change_from_year_high': stock.get_percent_change_from_year_high(),
        'percent_change_from_year_low': stock.get_percent_change_from_year_low(),
        'change_from_year_low': stock.get_change_from_year_low(),
        'change_from_year_high': stock.get_change_from_year_high(),
        'percent_change_from_200_day_moving_average': stock.get_percent_change_from_200_day_moving_average(),
        'change_from_200_day_moving_average': stock.get_change_from_200_day_moving_average(),
        'percent_change_from_50_day_moving_average': stock.get_percent_change_from_50_day_moving_average(),
        'change_from_50_day_moving_average': stock.get_change_from_50_day_moving_average(),
        'EPS_estimate_next_quarter': stock.get_EPS_estimate_next_quarter(),
        'EPS_estimate_next_year': stock.get_EPS_estimate_next_year(),
        'ex_dividend_date': stock.get_ex_dividend_date(),
        'EPS_estimate_current_year': stock.get_EPS_estimate_current_year(),
        'price_EPS_estimate_next_year': stock.get_price_EPS_estimate_next_year(),
        'price_EPS_estimate_current_year': stock.get_price_EPS_estimate_current_year(),
        'one_yr_target_price': stock.get_one_yr_target_price(),
        'change_percent_change': stock.get_change_percent_change(),
        'divended_pay_date': stock.get_dividend_pay_date(),
        'currency': stock.get_currency(),
        'last_trade_with_time': stock.get_last_trade_with_time(),
        'days_range': stock.get_days_range(),
        'years_range': stock.get_year_range()
    }
    return data

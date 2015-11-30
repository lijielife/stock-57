#!/usr/bin/python

import re
import os
import pickle
from datetime import datetime
from pprint import pprint
from yahoo_finance import Share

# The purpose of this class is to provide stock ticker's history data
# and the generic methods to deal with these data

class historical_stock_data:
    def __init__(self, ticker):
        self.name = ticker

        self.yahoo = Share(ticker)
        self.data_history_yahoo = []
        self.__update_data_history_from_yahoo()
        self.data_history_close = {}
        self.__get_history_close_from_yahoo()
        self.__add_daily_percent_change()

        self.price_data = {}
        self.dates = []

        description = "Get a stock ticker's historical data"

    def __update_data_history_from_yahoo(self):
        data_folder = "./data"
        data_ticker = data_folder + "/" + self.name + ".txt"

        start = "1950-01-01"
        end = datetime.fromordinal(datetime.today().toordinal()-1).\
              strftime("%Y-%m-%d") # yesterday
        today = datetime.today().strftime("%Y-%m-%d")

        # Use ticker as filename to store historical data into a text
        # file. only update the delta up to today
        print "Update %s historical data..." %self.name

        if not os.path.exists(data_folder):
            print "The data folder %s dose not exist!" %data_folder
            print "Create %s..." % data_folder
            os.mkdir(data_folder)

        if not os.path.exists(data_ticker):
            print "Create %s historical data from yahoo..." %self.name
            self.data_history_yahoo = self.yahoo.get_historical(start, end)
            self.data_history_yahoo.reverse()
            pickle.dump(self.data_history_yahoo, open(data_ticker, "wb"))
            return

        self.data_history_yahoo = pickle.load(open(data_ticker, "rb"))
        
        if not self.data_history_yahoo:
            print "Cannot get history data!"
            return

        prev_date = datetime.strptime(self.data_history_yahoo[-1]["Date"], \
            "%Y-%m-%d").strftime("%Y-%m-%d")

        if end > prev_date:
            print "Update %s data from %s to %s" %(self.name, prev_date, end)
            delta_history = self.yahoo.get_historical(prev_date, end)
            delta_history.reverse()
            self.data_history_yahoo += delta_history
            pickle.dump(self.data_history_yahoo, open(data_ticker, "wb"))
        else:
            print "Already up-to-date"

    def __get_history_close_from_yahoo(self):
        for item in self.data_history_yahoo:
            self.data_history_close[item["Date"]] = dict()
            self.data_history_close[item["Date"]]["Price"] = \
                float(item["Close"])

    def __add_daily_percent_change(self):
        prev = 0
        for key, value in sorted(self.data_history_close.items()):
            if prev == 0:
                prev = value["Price"]
            
            value["Change"] = (value["Price"] - prev) * 100 / prev
            prev = value["Price"]

    def print_today_price_from_yahoo(self):
        
        if not self.price_data:
            print "Price data is not available"
            return
        
        price_today = float(self.yahoo.get_price())
        prev = self.price_data[sorted(self.price_data.keys())[-1]]["Price"]
        chg = (price_today - prev) * 100 / prev
        print "%s price = %f change = %f" %(self.name, price_today, chg)

    def get_current_price_from_yahoo(self):
        return float(self.yahoo.get_price())
    
    def use_price_data_original(self):
        self.price_data = self.data_history_close
        self.dates = sorted(self.price_data.keys())

        print "Use original price data"


    # Remove the days that don't have significant changes in terms of
    # a threshold. 
    # 1. if day 2 has a change less than < threshold, day 2 will be discarsed
    # 2. day 3's change will be updated to a new percentage relative to day 1
    # 3. if day 3 has a change less than < threshold, day 3 will be discarsed
    # 4. This process will go on 
    def use_price_data_smoothed_by_percent(self, threshold):
        price_data = self.data_history_close
        prev = 0
        price_data_modified = {}
        
        for key, value in sorted(price_data.iteritems()):
            if prev == 0:
                prev = value["Price"]
                price_data_modified[key] = value;

            chg = (value["Price"] - prev) * 100 / prev

            if abs(chg) > threshold:
                value["Change"] = chg
                prev = value["Price"]
                price_data_modified[key] = value

        self.price_data = price_data_modified
        self.dates = sorted(self.price_data.keys())

        print "Use smoothed price data"

        return

    # Group price data as up and down
    # down days are grouped in a dict follows grouped up days
    def group_data_up_down(self, start, end):
        price_data = self.price_data
        up = {}
        down = {}
        prev = 0
        history_up_down = []

        for key, value in sorted(price_data.iteritems()):
            if key < start or key > end:
                continue

            if prev == 0:
                prev = value["Price"]

            if value["Price"] < prev:
                down[key] = value
                if up:
                    history_up_down.append(up)
                    up = {}
            else:
                up[key] = value
                if down:
                    history_up_down.append(down)
                    down = {}
            prev = value["Price"]
    
        # take care of the last item
        if down:
            history_up_down.append(down)

        if up:
            history_up_down.append(up)

        return history_up_down
    

    def get_data_days_of_down(self, history_up_down, down):
        days_of_down = {}
        for item in history_up_down:
            if down == 0:
                if item[item.keys()[0]]["Change"] > 0:
                    continue
            else:
                if item[item.keys()[0]]["Change"] < 0:
                    continue

            if days_of_down.get(len(item)):
                days_of_down[len(item.keys())] += 1
            else: # if no value yet, put 1
                days_of_down[len(item.keys())] = 1

        return days_of_down


    def get_data_dates_of_down(self, history_up_down, down):
        dates_of_down = {}

        for item in history_up_down:

            if down == 0:
                if item[item.keys()[0]]["Change"] > 0:
                    continue
            else:
                if item[item.keys()[0]]["Change"] < 0:
                    continue

            if not dates_of_down.get(len(item.keys())):
                dates_of_down[len(item.keys())] = []
            dates_of_down[len(item.keys())].append(item)
        
        return dates_of_down

    def add_probability_of_up_down(self, days_of_change):
        seq = sorted(days_of_change.keys())

        for i in seq:
            total = 0
            index = seq.index(i)
            for j in seq[index::]:
                total += float(days_of_change[j])
            p = (total - days_of_change[i]) / total
            days_of_change[i] = [days_of_change[i], p]
        pprint(days_of_change)

    def round_date_to_trading_date_start(self, start):
        for key in self.dates:
            if key >= start:
                break

        return key

    def round_date_to_trading_date_end(self, end):
        for key in reversed(self.dates):
            if key <= end:
                break

        return key

    def get_trading_dates(self, start, end):
        trading_dates = []

        for item in self.dates:
            if item >= start and item <= end:
                trading_dates.append(item)
        
        return trading_dates

    def __calc_trading_year_start_end(self):
        dates = self.dates
        year_start_end = {}
        year_start = dates[0]
        year_last = datetime.strptime(dates[0], "%Y-%m-%d").year

        for item in dates:
            year_this = datetime.strptime(item, "%Y-%m-%d").year
            if year_this != year_last:
                year_start_end[year_last] = [year_start, year_end]
                year_last = year_this
                year_start = item
            else:
                year_end = item
        year_start_end[year_this] = [year_start, year_end]

        return year_start_end
    
    def __calc_annual_list(self, t_start, t_end):
        year_start_end = self.__calc_trading_year_start_end()
        y_start = datetime.strptime(t_start, "%Y-%m-%d").year
        y_end = datetime.strptime(t_end, "%Y-%m-%d").year

        annual_list = {}
        if y_start == y_end:
            annual_list[y_start] = [t_start, t_end]
        elif y_start > y_end:
            print "invalid dates!"
        else:
            for item in range(y_start, (y_end + 1)):
                if item == y_start:
                    annual_list[item] = [t_start, year_start_end[item][1]]
                elif item == y_end:
                    annual_list[item] = [year_start_end[item][0], t_end]
                else:
                    annual_list[item] = year_start_end[item]

        return annual_list

    def __calc_total_return(self, t_start, t_end):
        start_price = self.price_data[t_start]["Price"]
        end_price = self.price_data[t_end]["Price"]

        return (end_price - start_price ) * 100 / start_price

    def calc_total_return(self, start, end):
        t_start = self.round_date_to_trading_date_start(start)
        t_end = self.round_date_to_trading_date_end(end)

        return self.__calc_total_return(t_start, t_end)

    def calc_annual_return(self, start, end):
        t_start = self.round_date_to_trading_date_start(start)
        t_end = self.round_date_to_trading_date_end(end)

        annual_list = self.__calc_annual_list(t_start, t_end)
        annual_return = {}

        for key, value in sorted(annual_list.iteritems()):
            annual_return[key] = self.__calc_total_return(*value)

        return annual_return

    def get_available_trading_dates(self):
        return sorted(self.data_history_close.keys())

    def get_stock_price(self, date):
        return self.data_history_close[date]["Price"]

    def print_stock_price(self, date):
        print "date %s close price %6.2f change %6.2f" %(\
            date,
            self.data_history_close[date]["Price"], \
            self.data_history_close[date]["Change"])

    def test(self):
        self.use_price_data_original()
        self.print_today_price_from_yahoo()
        self.use_price_data_smoothed_by_percent(1)

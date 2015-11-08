#!/usr/bin/python

import re
import os
import pickle
from datetime import datetime
from pprint import pprint
from yahoo_finance import Share

class yahoo_historical_analysis:

    def __init__(self, ticker):
        self.yesterday = datetime.fromordinal(datetime.today().toordinal()-1).strftime("%Y-%m-%d")
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.start = "1950-01-01"
        self.ticker = ticker
        self.data_history = []
        self.data_history_close = {}
        self.__update_data_history(ticker, self.start, self.yesterday)
        self.__update_percent_change_of_one_day()

        description = "Get a stock ticker's historical data from yahoo"

    def __update_data_history(self, ticker, start, end):
        self.yahoo = Share(ticker)
        data_folder = "./data"
        data_ticker = data_folder + "/" + ticker + ".txt"

        # Use ticker as filename to store historical data into a text
        # file. only update the delta up to today
        print "Update %s historical data..." %ticker

        if not os.path.exists(data_folder):
            print "The data folder %s dose not exist!" %data_folder
            print "Create %s..." % data_folder
            os.mkdir(data_folder)

        if not os.path.exists(data_ticker):
            print "Create %s historical data from yahoo..." %ticker
            self.data_history = self.yahoo.get_historical(start, end)
            self.data_history.reverse()
            pickle.dump(self.data_history, open(data_ticker, "wb"))
            return

        self.data_history = pickle.load(open(data_ticker, "rb"))
        
        if not self.data_history:
            print "Cannot get history data!"
            return

        prev_date = datetime.strptime(self.data_history[-1]["Date"], "%Y-%m-%d").strftime("%Y-%m-%d")

        if end > prev_date:
            print "Update %s data from %s to %s" %(ticker, prev_date, end)
            delta_history = self.yahoo.get_historical(prev_date, end)
            delta_history.reverse()
            self.data_history += delta_history
            pickle.dump(self.data_history, open(data_ticker, "wb"))
        else:
            print "Already up-to-date"

        for item in self.data_history:
            self.data_history_close[item["Date"]] = dict()
            self.data_history_close[item["Date"]]["Price"] = float(item["Close"])

    def __update_percent_change_of_one_day(self):
        prev = 0
        for key, value in sorted(self.data_history_close.items()):
            if prev == 0:
                prev = value["Price"]
            
            value["Change"] = (value["Price"] - prev) * 100 / prev
            prev = value["Price"]

    # Remove the days that don't have significant changes in terms of
    # a threshold. 
    # 1. if day 2 has a change less than < threshold, day 2 will be discarsed
    # 2. day 3's change will be updated to a new percentage relative to day 1
    # 3. if day 3 has a change less than < threshold, day 3 will be discarsed
    # 4. This process will go on 
    def smooth_by_hold(self, price_data, threshold):
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

        print len(price_data.keys())
        print len(price_data_modified.keys())

        return price_data_modified

    def change_of_today(self, price_data):
        price_today = float(self.yahoo.get_price())
        prev = price_data[sorted(price_data.keys())[-1]]["Price"]
        chg = (price_today - prev) * 100 / prev
        print "%s price = %f change = %f" %(self.ticker, price_today, chg)
        
    # Group price data as up and down
    # down days are grouped in a dict follows grouped up days
    def group_history_data_up_down(self, price_data):
        up = {}
        down = {}
        prev = 0
        history_up_down = []

        for key, value in sorted(price_data.iteritems()):
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

    # with 3 days down, what is the next up, and what is the drop
    # after that


from dateutil.relativedelta import relativedelta


class benchmark_and_strategies:
    def __init__(self, ticker):
        self.ticker = yahoo_historical_analysis(ticker)
        self.history_smooth = self.ticker.smooth_by_hold(self.ticker.data_history_close, 1)
        self.history_up_down = self.ticker.group_history_data_up_down(self.history_smooth)
        self.history_days_down = self.ticker.get_data_days_of_down(self.history_up_down, 0)
        self.history_days_up = self.ticker.get_data_days_of_down(self.history_up_down, 1)
        self.history_dates_down = self.ticker.get_data_dates_of_down(self.history_up_down, 0)
        self.history_dates_up = self.ticker.get_data_dates_of_down(self.history_up_down, 1)

    def report_history(self):
        pprint(self.history_days_down)
        pprint(self.history_days_up)
        pprint(self.history_dates_down)
        pprint(self.history_dates_up)


    def benchmark_total_gain(self, start, end):
        total_gain = 1

        #for key, value in sorted(self.ticker.data_history_close.items()):
        for key, value in sorted(self.history_smooth.items()):
            if key >= start and key <= end:
                total_gain *= (100 + value["Change"]) / 100
        
        return total_gain

    def benchmark_annual_return(self, start, end):
        total_gain = self.benchmark_total_gain(start, end)
        annual_list = self.__benchmark_year(start, end)
        accum_gain = 1

        for item in annual_list:
            annual_gain = self.benchmark_total_gain(*item)
            accum_gain *= annual_gain
            print annual_gain, accum_gain

    def __benchmark_year(self, start, end):
        annual_list = []
        year_start = datetime.strptime(start, "%Y-%m-%d").year
        year_end = datetime.strptime(end, "%Y-%m-%d").year
        
        for year in range(year_start, (year_end + 1)):
            y_first = str(year) + "-01-01"
            y_last = str(year) + "-12-31"
            if year == year_start:
                annual_list.append([start, y_last])
            elif year == year_end:
                annual_list.append([y_first, end])
            else:
                annual_list.append([y_first, y_last])

        return annual_list

    def strategy_3_days(self, start):

        flag_3d = 0
        flag_u = 0
        gain = 1

        for item in self.history_up_down:
            if (item[item.keys()[0]]["Change"] < 0) and \
               (len(item.keys()) == 3 or \
                len(item.keys()) == 4 or \
                len(item.keys()) == 2):
                flag_3d = 1
                print "3 days down"
                pprint(item)
            if (item[item.keys()[0]]["Change"] > 0) and \
               (flag_3d == 1) :
                flag_3d = 0
                flag_u = 1
                print "the following up"
                pprint(item)

                if item.keys()[0] > start:
                    for key, value in sorted(item.iteritems()):
                        gain *= (100 + value["Change"]) / 100
                    print gain

            if (item[item.keys()[0]]["Change"] < 0) and \
               (flag_u == 1) :
                flag_u = 0
                print "the following down"
                pprint(item)
                if item.keys()[0] > start:
                    gain *= (100 + item[item.keys()[0]]["Change"]) / 100
                print gain



# pprint(dates_of_down)
# pprint(dates_of_up)
gspc = benchmark_and_strategies('^GSPC')
print gspc.benchmark_total_gain("1999-01-01", "2015-11-05")
print gspc.benchmark_annual_return("1999-01-01", "2015-11-05")

#gspc.change_of_today(history_data_rm)


#print qcom.yahoo.get_price()

#!/usr/bin/python

import re
from datetime import datetime
from pprint import pprint

sp500_data = []

with open('sp500-history.csv') as file:
    sp500_data = file.readlines()


def convert_csv_to_array( sp500_data ):
    "convert each line to arry with closing price"
    sp500_array = []
    
    for line in sp500_data:
        tmp = line.split(',')
        tmp[6] = tmp[6].rstrip('\r\n')
        tmp[6] = float(tmp[6])
        
        sp500_array.insert(0, [datetime.strptime(tmp[0],"%m/%d/%Y").strftime("%Y%m%d"), tmp[6]])

    return sp500_array

sp500_array = convert_csv_to_array(sp500_data)

# for tmp in sp500_array:
#     print tmp[0], tmp[1]

def find_alltime_highs(sp500_array):
    "find sp500 all time highs"
    sp500_alltime_highs = []
    max = 0

    for i in range(0, len(sp500_array)):
        cur = sp500_array[i][1]
        if cur > max:
            max = cur
            sp500_array[i].append(i)
            sp500_alltime_highs.append(sp500_array[i])

    return sp500_alltime_highs

sp500_alltime_highs = find_alltime_highs(sp500_array)

# for tmp in sp500_alltime_highs:
#     print tmp;

def linear_between_highs(sp500_array, sp500_alltime_highs):
    "find the lowest betwee 2 highs"
    for i in range (0, (len(sp500_alltime_highs) - 1)):
        
        min = sp500_alltime_highs[i][1]
        decrease_array = []

        for j in range(sp500_alltime_highs[i][2] + 1,
                       sp500_alltime_highs[i+1][2]):
            cur = sp500_array[j][1]
            if cur < min :
                 min = cur
                 sp500_array[j].append(j)
                 decrease_array.append(sp500_array[j])
        
        if not decrease_array:
            continue
                 
        sp500_alltime_highs[i].append(decrease_array)

        max = decrease_array[-1][1]
        increase_array = []

        for j in range(decrease_array[-1][2],
                       sp500_alltime_highs[i+1][2]):
            cur = sp500_array[j][1]
            if cur > max:
                max = cur
                sp500_array[j].append(j)
                increase_array.append(sp500_array[j])

        if not increase_array:
            continue
            
        sp500_alltime_highs[i].append(increase_array)
        

linear_between_highs(sp500_array, sp500_alltime_highs);

# for tmp in sp500_alltime_highs:
#     print tmp[0], tmp[1]

#     if len(tmp) == 3:
#         continue
    
#     for i in range(0, len(tmp[3])):
#         print tmp[3][i][0], tmp[3][i][1]

#     if len(tmp) == 4:
#         continue
    
#     for i in range(0, len(tmp[4])):
#         print tmp[4][i][0], tmp[4][i][1]

# for tmp in sp500_alltime_highs:
#     print tmp;

    


# sp500_m_d = find_sp500_month_data(sp500_data)

# for num in range (1, len(sp500_m_d)):
#     print sp500_m_d[-num].strip('\n')

# def find_sp500_month_data( sp500_data ):
#     "reduce data set including only the last day of each month"

#     sp500_data_month = []
#     month_pre = 0
    
#     for line in sp500_data:
#         month = re.match( r'^(.*?)\/', line, re.M|re.I)
#         if month :
#             month_cur = int(month.group(1))
#             if month_cur != month_pre:
#                 sp500_data_month.append(line)
#                 month_pre = month_cur

#     return sp500_data_month

import os
import pickle
from yahoo_finance import Share

# yahoo = Share("^GSPC")
# print yahoo.get_price()

# pprint(yahoo.get_historical('1949-11-01', datetime.today().strftime("%Y-%m-%d")))


class yahoo_historical_analysis:
    data_down = []
    data_down_of_days = {}
    data_up = []
    data_history_close = {}
    
    def __init__(self,ticker):
        self.yesterday = datetime.fromordinal(datetime.today().toordinal()-1).strftime("%Y-%m-%d")
        self.today = datetime.today().strftime("%Y-%m-%d")
        self.start = "1950-01-01"
        self.ticker = ticker
        self.data_history = []
        self.__update_data_history(ticker, self.start, self.yesterday)
        description = "Get a stock ticker's historical data from yahoo"

    def __update_data_history(self, ticker, start, end):
        yahoo = Share(ticker)
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
            self.data_history = yahoo.get_historical(start, end)
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
            delta_history = yahoo.get_historical(prev_date, end)
            delta_history.reverse()
            self.data_history += delta_history
            pickle.dump(self.data_history, open(data_ticker, "wb"))
        else:
            print "Already up-to-date"

        for i in range(0, len(self.data_history)):
            self.data_history_close[self.data_history[i]["Date"]] = self.data_history[i]["Close"]

    def get_downward_stat(self):
        keys = self.data_history_close.keys()
        keys.sort()

        down = {}
        prev_price = self.data_history_close[keys[0]]
        for key in keys:
            if self.data_history_close[key] < prev_price:
                down[key] = self.data_history_close[key]
            else:
                if down:
                    self.data_down.append(down)
                    down = {}
            prev_price = self.data_history_close[key]

        for item in self.data_down:
            if self.data_down_of_days.get(len(item)):
                self.data_down_of_days[len(item)] += 1
            else:
                self.data_down_of_days[len(item)] = 1

        pprint(self.data_down_of_days)

gspc = yahoo_historical_analysis("^GSPC")
# qcom = yahoo_historical_analysis("QCOM")

gspc.get_downward_stat()

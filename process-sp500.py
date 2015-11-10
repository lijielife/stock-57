#!/usr/bin/python

import re
import os
import pickle
from datetime import datetime
from pprint import pprint
from yahoo_finance import Share

class yahoo_historical_analysis:

    def __init__(self, ticker):
        self.yesterday = datetime.fromordinal(datetime.today().toordinal()-1).\
                         strftime("%Y-%m-%d")
        self.today = datetime.today().strftime("%Y-%m-%d")

        self.start = "1950-01-01"
        self.ticker = ticker
        self.data_history = []
        self.data_history_close = {}

        self.__update_data_history(ticker, self.start, self.yesterday)
        self.__update_percent_change_of_one_day()

        self.history_smooth = self.smooth_by_hold(self.data_history_close, 1)
        self.history_up_down = self.group_history_data_up_down(self.history_smooth)
        self.history_days_down = self.get_data_days_of_down(self.history_up_down, 0)
        self.history_days_up = self.get_data_days_of_down(self.history_up_down, 1)
        self.history_dates_down = self.get_data_dates_of_down(self.history_up_down, 0)
        self.history_dates_up = self.get_data_dates_of_down(self.history_up_down, 1)
        self.add_probability_of_up_down(self.history_days_down)
        self.add_probability_of_up_down(self.history_days_up)

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

    def report_history_up_down(self):
        print "===Report history up down"
        pprint(self.history_up_down)
        print "===Report statistics for each down:"
        pprint(self.history_days_down)
        pprint(self.history_dates_down)
        print "===Report statistics for each up:"
        pprint(self.history_days_up)
        pprint(self.history_dates_up)


class benchmark_and_strategies:
    def __init__(self, ticker):
        self.ticker = yahoo_historical_analysis(ticker)
        self.s1_long = {3: 10, \
                        4: 20, \
                        5: 40, \
                        6: 80, \
                        7: 160, \
                        8: 160, \
                        9: 160, \
                        10: 160}

    def report_history(self):
        pprint(self.history_days_down)
        pprint(self.history_days_up)
        pprint(self.history_dates_down)
        pprint(self.history_dates_up)


    def __calc_year(self, start, end):
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

    def __calc_return(self, price_data, start, end):
        gain = 0

        for key in sorted(price_data.keys()):
            if key >= start:
                break
        start_price = price_data[key]["Price"]

        for key in reversed(sorted(price_data.keys())):
            if key <= end:
                break
        end_price = price_data[key]["Price"]

        gain = (end_price - start_price ) * 100 / start_price

        return gain

    def calc_benchmark_total_return(self, start, end):
        return self.__calc_return(self.ticker.data_history_close, start, end)

    def calc_benchmark_annual_return(self, start, end):
        annual_list = self.__calc_year(start, end)
        annual_return = []

        for item in annual_list:
            annual_gain = self.__calc_return(self.ticker.data_history_close, \
                                             *item)
            annual_return.append([item, annual_gain])

        return annual_return

    def __s1_get_long_positions(self, start, end, days_of_down):
        list_buy = []
        long_positions = []

        # find dates when price is down for more than 3 days
        for item in self.ticker.history_up_down:
            if item[item.keys()[0]]["Change"] < 0 and \
               len(item.keys()) == days_of_down and \
               sorted(item.keys())[days_of_down - 1] > start:
                list_buy.append(item)

        for item in list_buy:
            if len(item.keys()) == days_of_down:
                pprint(item)
                pos = {}

                buy_date = sorted(item.keys())[days_of_down -1]
                buy_price = item[buy_date]["Price"]
                buy_total = buy_price * self.s1_long[days_of_down]

                pos["B"] = [buy_date, buy_price, buy_total]
                long_positions.append(pos)

        return long_positions

    # strategy 1:
    def backtest_strategy_1(self, start, end):
        print "Stratege 1"

        price_data = self.ticker.history_smooth
        strategy_pos = self.__s1_get_long_positions(start, end, 7)


        for item in strategy_pos:
            buy_date = item["B"][0]
            buy_price = item["B"][1]
            buy_total = item["B"][2]

            sell_date = self.backtest_strategy_1_sell(buy_date)
            if sell_date:
                sell_price = price_data[sell_date]["Price"]
                sell_total = sell_price / buy_price * buy_total
                sell_gain = (sell_price - buy_price) / buy_price * 100

                item["S"] = [sell_date, sell_price, sell_total, sell_gain]
        pprint(strategy_pos)

    # find sell date a start date
    # 1. only after an "up"
    # 2. the first down after that
    # 3. the total return has to be > 1%
    def backtest_strategy_1_sell(self, start):
        price_data = self.ticker.history_smooth

        date = sorted(price_data.keys())
        init = price_data[start]["Price"]
        prev = init

        up = 0
        down = 0
        sell_date = ""

        for key in date[(date.index(start) + 1)::]:
            price = price_data[key]["Price"]

            if price < prev:
                down = 1
                if up == 1:     # from previous up
                    if ((price - init) * 100 / init) > 1:
                        sell_date = key
                        break
                up = 0
            else:
                down = 0
                up = 1
            prev = price

        return sell_date

gspc = benchmark_and_strategies('^GSPC')
# gspc.ticker.report_history_up_down()
gspc.ticker.report_history_up_down()
print gspc.calc_benchmark_total_return("1999-01-01", "2015-11-05")
pprint(gspc.calc_benchmark_annual_return("1999-01-01", "2015-11-05"))

gspc.backtest_strategy_1("1999-01-01", "2015-11-05")

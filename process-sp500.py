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
        # print "===Report statistics for each down:"
        # pprint(self.history_days_down)
        # pprint(self.history_dates_down)
        # print "===Report statistics for each up:"
        # pprint(self.history_days_up)
        # pprint(self.history_dates_up)


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

    def __calc_trading_date_start_end(self, dates, start, end):
        for key in dates:
            if key >= start:
                break
        t_start = key

        for key in reversed(dates):
            if key <= end:
                break
        t_end = key
        
        return [t_start, t_end]

    def __calc_trading_year_start_end(self, dates):
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
    
    def __calc_annual_list(self, dates, t_start, t_end):
        year_start_end = self.__calc_trading_year_start_end(dates)
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

    def __calc_return(self, price_data, t_start, t_end):
        start_price = price_data[t_start]["Price"]
        end_price = price_data[t_end]["Price"]

        return (end_price - start_price ) * 100 / start_price

    def calc_benchmark_total_return(self, start, end):
        price_data = self.ticker.data_history_close
        dates = sorted(price_data.keys())
        t_start_end =  self.__calc_trading_date_start_end(dates, start, end)

        return self.__calc_return(price_data, *t_start_end)

    def calc_benchmark_annual_return(self, start, end):
        price_data = self.ticker.data_history_close
        dates = sorted(price_data.keys())
        t_start_end =  self.__calc_trading_date_start_end(dates, start, end)
        annual_list = self.__calc_annual_list(dates, *t_start_end)

        annual_return = {}

        for key, value in sorted(annual_list.iteritems()):
            annual_gain = self.__calc_return(price_data, *value)
            annual_return[key] = annual_gain

        return annual_return

    def calc_strategy_annual_return(self, start, end):
        price_data = self.ticker.history_smooth
        dates = sorted(price_data.keys())
        t_start_end =  self.__calc_trading_date_start_end(dates, start, end)
        list_tran = self.__s1_get_transactions(*t_start_end)

        for item in list_tran:
            pprint(item)
            total_gain = self.__calc_return(price_data, *item)
            print "total=%f" %total_gain
            annual_list = self.__calc_annual_list(dates, *item)
            annual_gain = {}
            pprint(annual_list)
            for key, value in sorted(annual_list.iteritems()):
                annual_gain[key] = self.__calc_return(price_data, *value)
            pprint(annual_gain)
            print "====="


    # find buy date
    # only after down dates (more than days_of_down
    # only the up after that
    # that up is smaller than the previous down
    def __s1_get_buy_dates(self, start, end):
        days_of_down = 2
        price_data_grouped = self.ticker.history_up_down
        print "++++"
        pprint(price_data_grouped)
        print "++++"
        list_buy = []

        # find dates when price is down for more than days_of_down days
        for item in price_data_grouped:
            days = sorted(item.keys())

            if item[days[0]]["Change"] < 0 and \
               len(days) >= days_of_down and \
               days[days_of_down - 1] >= start:
                
                idx = price_data_grouped.index(item)
                next_item = price_data_grouped[idx + 1]
                next_item_1st = sorted(next_item.keys())[0]
                list_buy.append(next_item_1st)
                # buy_price = next_item[next_item_1st]["Price"]
                # down_days = len(days)
                # down_init = item[days[0]]["Price"]
                # down_last = item[days[len(days) - 1]]["Price"]
                # down_pctg = (down_last - down_init) * 100 / down_init
                # up_pctg = next_item[next_item_1st]["Change"]

                # # if ads(down_pctg) < 3 and len(days) == 2:
                # #     continue
                # list_buy[next_item_1st] = [buy_price, down_days, \
                #                            down_init, down_pctg, \
                #                            down_last, up_pctg]
        return list_buy

    # find sell date by a start date
    # 1. only after an "up"
    # 2. the first down after that
    # 3. the total return has to be > gain
    def __s1_get_sell_date(self, start):
        gain = 1
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
                    if ((price - init) * 100 / init) > gain:
                        sell_date = key
                        break
                up = 0
            else:
                down = 0
                up = 1
            prev = price

        return sell_date

    def __s1_get_transactions(self, start, end):
        price_data = self.ticker.history_smooth
        list_transactions = []

        list_buy = self.__s1_get_buy_dates(start, end)
        
        for item in sorted(list_buy):
            sell_date = self.__s1_get_sell_date(item)
            if not sell_date:
                continue

            list_transactions.append([item, sell_date])

            # sell_price = price_data[sell_date]["Price"]
            # sell_gain = (sell_price - value[0]) / value[0] * 100
            # hold_peroid = datetime.strptime(sell_date, "%Y-%m-%d") - \
            #               datetime.strptime(key, "%Y-%m-%d")
            # transaction["B"] = [key, value]
            # transaction["S"] = [sell_date, [sell_price, sell_gain, hold_peroid.days]]
            # list_transactions.append(transaction)

        return list_transactions

    # def backtest_strategy(self, start, end):
    #     print "Stratege 1"

    #     price_data = self.ticker.history_smooth
    #     dates =  sorted(price_data.keys())
    #     list_buy = self.__s1_get_buy_dates(start, end, 2)
    #     list_tran = self.__s1_get_transactions(list_buy)
    #     pprint(list_tran)

    #     for item in list_tran:
    #         buy_date = item["B"][0]
    #         buy_amt = item["B"][0][0] * 100
    #         sell_date = item["S"][0]

backtest_period = ["2005-01-01", "2015-11-08"]
gspc = benchmark_and_strategies('^GSPC')
# print gspc.calc_benchmark_total_return(*backtest_period)
# pprint(gspc.calc_benchmark_annual_return(*backtest_period))

spy = benchmark_and_strategies('SPY')
# pprint(spy.ticker.report_history_up_down())

#spy.backtest_strategy(*backtest_period)
pprint(spy.calc_benchmark_annual_return(*backtest_period))
print spy.calc_benchmark_total_return(*backtest_period)
print spy.calc_strategy_annual_return(*backtest_period)

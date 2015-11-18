#!/usr/bin/python

import re
import os
import pickle
from datetime import datetime
from pprint import pprint
from yahoo_finance import Share

# The purpose of this class is to provide ticker's history data
class yahoo_historical_analysis:
    def __init__(self, ticker):
        self.name = ticker

        self.yahoo = Share(ticker)
        self.data_history_yahoo = []
        self.__update_data_history_from_yahoo()
        self.data_history_close = {}
        self.__get_history_close_from_yahoo()

        self.__add_daily_percent_change()
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

    def get_today_price_from_yahoo(self):
        price_data = self.data_history_close
        price_today = float(self.yahoo.get_price())
        prev = price_data[sorted(price_data.keys())[-1]]["Price"]
        chg = (price_today - prev) * 100 / prev
        print "%s price = %f change = %f" %(self.name, price_today, chg)
        
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

    def test(self):
        print "===Report history up down"
        self.get_today_price_from_yahoo()
        # self.history_smooth = self.smooth_by_hold(self.data_history_close, 1)
        # self.history_up_down = self.group_history_data_up_down(self.history_smooth)
        # self.history_days_down = self.get_data_days_of_down(self.history_up_down, 0)
        # self.history_days_up = self.get_data_days_of_down(self.history_up_down, 1)
        # self.history_dates_down = self.get_data_dates_of_down(self.history_up_down, 0)
        # self.history_dates_up = self.get_data_dates_of_down(self.history_up_down, 1)
        # self.add_probability_of_up_down(self.history_days_down)
        # self.add_probability_of_up_down(self.history_days_up)

        # print "===Report statistics for each down:"
        # pprint(self.history_days_down)
        # pprint(self.history_dates_down)
        # print "===Report statistics for each up:"
        # pprint(self.history_days_up)
        # pprint(self.history_dates_up)


class benchmark_and_strategies:
    def __init__(self, ticker):
        self.ticker = yahoo_historical_analysis(ticker)
        self.fund = {}
        self.ticker.test()
        

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

    def __s1_get_buy_dates(self, price_data, start, end):

        days_of_down = 2
        price_data_grouped = self.ticker.group_history_data_up_down(price_data)
        list_buy = []

        # find dates when price is down for more than days_of_down days
        for item in price_data_grouped:
            days = sorted(item.keys())
            amount = 100
            buys = {}

            if item[days[0]]["Change"] < 0 and \
               len(days) >= days_of_down and \
               days[days_of_down - 1] >= start:
                
                idx = price_data_grouped.index(item)
                next_idx = idx + 1
                if next_idx < (len(price_data_grouped) - 1):
                    next_item = price_data_grouped[next_idx]
                    next_item_1st = sorted(next_item.keys())[0]
                    # todo: amount algorithm
                    list_buy.append([next_item_1st, amount])

        return list_buy

    # find sell date by a start date
    # 1. only after an "up"
    # 2. the first down after that
    # 3. the total return has to be > gain
    def __s1_get_sell_date(self, price_data, start):
        gain = 1
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

    def __s1_get_transactions(self, price_data, start, end):
        list_transactions = []
        list_buy = self.__s1_get_buy_dates(price_data, start, end)
        
        for item in sorted(list_buy):
            sell_date = self.__s1_get_sell_date(price_data, item[0])

            if not sell_date:
                continue

            list_transactions.append([item, sell_date])

        return list_transactions


    def calc_strategy_annual_return(self, price_data, list_tran, start, end):
        dates = sorted(price_data.keys())
        t_start_end =  self.__calc_trading_date_start_end(dates, start, end)
        list_result = []

        for item in list_tran:
            total_gain = self.__calc_return(price_data, *item)
            annual_list = self.__calc_annual_list(dates, *item)
            annual_gain = {}
            for key, value in sorted(annual_list.iteritems()):
                annual_gain[key] = self.__calc_return(price_data, *value)
            list_result.append([annual_list, annual_gain])

        return list_result

    # def calc_s1_strategy(self, start, end):
    #     price_data = self.ticker.history_smooth
    #     orig_dates = sorted(price_data.keys())
    #     t_start_end =  self.__calc_trading_date_start_end(orig_dates, start, end)
    #     list_tran = self.__s1_get_transactions(price_data, *t_start_end)
        
    #     dates = orig_dates[orig_dates.index(t_start_end[0]): orig_dates.index(t_start_end[1]):]
    #     pprint(dates)

    #     fund = {}
    #     prev = {}
    #     prev["Invest"] = 0
    #     prev["Equity"] = 0
    #     prev["Liquid"] = 0

    #     for key in dates:
    #         current = {}

    #         for item in list_tran:
    #             date_long = item[0][0]
    #             unit_long = item[0][1]
    #             date_sell = item[1]

    #             if key == long_date: # a new position
    #                 amt_long = unit_long * price_data[date_long]["Price"]
    #                 if amt_long > prev["Liquid"]:
    #                     current["Invest"] += amt_long - prev["Liquid"]
    #                     current["Liquid"] = 0
    #                 else:
    #                     current["Liquid"] = prev["Liquid"] - amt_long
                        
    #                 current["Equity"] =  prev["Equity"] + unit_long * price_data[key]["Price"]
    #                 fund[key] = current;
    #                 prev = current
    #             elif key == date_sell:
                    

    #         print key
    #         pprint(positions)

# position
# "id": 2015-11-18-spy
# "ticker": spy
# "date": 2015-11-18
# "type": "long"
# "unit": 100

# "id": 2015-11-18-spy
# "ticker": spy
# "date": 2015-11-18
# "type": "sell"
# "unit": 100

# class track_fund_and_positions:
#     def __init__(self):
#         self.positions = {}
#         self.fund = {}
        
#     def add_position(self, position):
#         positions.append
    
        #     long_amt = amount * price_data[long_date]["Price"] - \
        #                fund[long_date]["Liquid"]

        #     sell_amt = amount * price_data[sell_date]["Price"]
        #     idx_long = dates.index(long_date)
        #     idx_sell = dates.index(sell_date)

        #     for key in dates[idx_long::]:
        #         if long_amt > 0:
        #             fund[key]["Invest"] += long_amt
        #         else:
        #             fund[key]["Liquid"] += long_amt

        #         if key < sell_date:
        #             fund[key]["Equity"] += amount * price_data[key]["Price"]
        #         elif key == sell_date:
        #             fund[key]["Liquid"] += sell_amt
        #         else:
        #             fund[key]["Liquid"] += sell_amt

        # fund["Invest"] = 0
        # fund["Liquid"] = 0
        # fund["Equity"] = 0
        
backtest_period = ["2015-01-01", "2015-11-08"]
spy = benchmark_and_strategies('SPY')
pprint(spy.calc_benchmark_annual_return(*backtest_period))
print spy.calc_benchmark_total_return(*backtest_period)
# pprint(spy.calc_s1_strategy(*backtest_period))


# pprint(spy.ticker.report_history_up_down())
#spy.backtest_strategy(*backtest_period)
#gspc = benchmark_and_strategies('^GSPC')
# print gspc.calc_benchmark_total_return(*backtest_period)
# pprint(gspc.calc_benchmark_annual_return(*backtest_period))

    


#!/usr/bin/python
import re
import os
import pickle
from datetime import datetime
from pprint import pprint
from yahoo_finance import Share
from stock_data import historical_stock_data

class spy_strategies:
    def __init__(self, ticker, period):
        self.ticker = historical_stock_data(ticker)
        self.ticker.use_price_data_smoothed_by_percent(1)
        #self.ticker.use_price_data_original()
        self.period = period

        self.trading_dates = self.ticker.get_trading_dates(*period)
        self.date_start = self.trading_dates[0]
        self.date_end = self.trading_dates[-1]
        
        print self.date_start, self.date_end

        self.annual_list = self.ticker.calc_annual_list(\
            self.date_start, self.date_end)
        pprint(self.annual_list)

        print self.ticker.calc_total_return(self.date_start, self.date_end)
        print self.ticker.calc_annual_return(self.date_start, self.date_end)
        
        self.price_data_grouped = \
            self.ticker.group_data_up_down(self.date_start, self.date_end)

        self.positions = []

    def __get_long_date(self):
        price_data_grouped = self.price_data_grouped
        start = self.date_start
        end = self.date_end

        days_of_down = 2

        # find dates when price is down for more than days_of_down days
        for item in price_data_grouped:
            days = sorted(item.keys())
            position = {}

            if item[days[0]]["Change"] < 0 and \
               len(days) >= days_of_down and \
               days[days_of_down - 1] >= start:
                
                idx = price_data_grouped.index(item)
                next_idx = idx + 1
                if next_idx < (len(price_data_grouped) - 1):
                    next_item = price_data_grouped[next_idx]
                    next_item_1st = sorted(next_item.keys())[0]
                    # todo: amount algorithm
                    position["start-date"] = next_item_1st
                    position["type"] = "long"
                    position["ticker"] = self

                    self.positions.append(position)

    # find sell date by a start date
    # 1. only after an "up"
    # 2. the first down after that
    # 3. the total return has to be > gain
    def __get_sell_date(self, start):
        price_data = self.ticker.price_data
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

    def __get_pos_unit(self, date):
        return 100

    def __get_pos_price(self, date):
        return self.ticker.price_data[date]["Price"]

    def get_positions(self):
        # setup position dates
        self.__get_long_date()

        for item in self.positions:
            item["units"] = self.__get_pos_unit(item["start-date"])
            item["start-price"] = self.__get_pos_price(item["start-date"])
            close_date = self.__get_sell_date(item["start-date"])
            if not close_date:
                continue

            item["close-date"] = close_date
            item["close-price"] = self.__get_pos_price(close_date)

        return self.positions
        

    # def calc_strategy_annual_return(self, price_data, list_tran, start, end):
    #     dates = sorted(price_data.keys())
    #     t_start_end =  self.__calc_trading_date_start_end(dates, start, end)
    #     list_result = []

    #     for item in list_tran:
    #         total_gain = self.__calc_return(price_data, *item)
    #         annual_list = self.__calc_annual_list(dates, *item)
    #         annual_gain = {}
    #         for key, value in sorted(annual_list.iteritems()):
    #             annual_gain[key] = self.__calc_return(price_data, *value)
    #         list_result.append([annual_list, annual_gain])

    #     return list_result

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
        
# backtest_period = ["2015-01-01", "2015-11-08"]
# pprint(spy.calc_benchmark_annual_return(*backtest_period))
# print spy.calc_benchmark_total_return(*backtest_period)
# pprint(spy.calc_s1_strategy(*backtest_period))
# pprint(spy.ticker.report_history_up_down())
#spy.backtest_strategy(*backtest_period)
#gspc = benchmark_and_strategies('^GSPC')
# print gspc.calc_benchmark_total_return(*backtest_period)
# pprint(gspc.calc_benchmark_annual_return(*backtest_period))

    


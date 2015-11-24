#!/usr/bin/python
import re
import os
import pickle
from datetime import datetime
from pprint import pprint
from yahoo_finance import Share
from stock_data import historical_stock_data

class spy_strategy:
    def __init__(self, ticker, period):
        self.ticker = ticker
        self.ticker.use_price_data_smoothed_by_percent(1)
        #self.ticker.use_price_data_original()
        self.period = period

        self.trading_dates = self.ticker.get_trading_dates(*period)
        self.date_start = self.trading_dates[0]
        self.date_end = self.trading_dates[-1]
        
        print self.date_start, self.date_end
        
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

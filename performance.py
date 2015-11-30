#!/usr/bin/python
import re
import os
import pickle
from datetime import datetime
from pprint import pprint
from operator import itemgetter
from yahoo_finance import Share
from stock_data import historical_stock_data
from strategy import spy_strategy

class performance:
    def __init__(self, ticker):
        self.ticker = ticker
        self.positions = []
        self.fund_hist = {}
        self.perf_hist = {}
        
    def add_positions(self, positions):
        self.positions.extend(positions)
        self.positions.sort(key=itemgetter('start-date'))

        for item in self.positions:
            self.__print_position(item)

        dates = self.ticker.get_available_trading_dates()
        self.dates = dates[dates.index(self.positions[0]["start-date"])::]

        for item in self.positions:
            self.__print_position(item)

    def __print_position(self, item):
        if not item:
            return

        if item.get("close-date"):
            gain = (item["close-price"] - item["start-price"]) \
                       / item["start-price"] * 100

            print "symbol:%s type:%s %s %f %s %f gain=%f" \
                %(self.ticker.name, \
                  item["type"], 
                  item["start-date"],
                  item["start-price"],
                  item["close-date"],
                  item["close-price"],
                  gain)
        else:
            today_date = datetime.today().strftime("%Y-%m-%d")
            today_price = self.ticker.get_current_price_from_yahoo()
            gain = (today_price - item["start-price"]) \
                   / item["start-price"] * 100

            print "symbol:%s type:%s %s %f open:%s %f gain=%s" \
                %(self.ticker.name, \
                  item["type"], 
                  item["start-date"],
                  item["start-price"],
                  today_date,
                  today_price,
                  gain)

    def __print_perf(self, item):
        if not item:
            return
            
        gain = (item["liquid"] + item["equity"] - item["invest"]) * 100 /\
               item["invest"]

        print "invest %6.2f liquid %6.2f equity %6.2f gain %3.2f" %(\
            item["invest"], item["liquid"], item["equity"], gain)

    def __print_fund(self, fund):
        if not fund:
            return

        for key, value in fund.iteritems():
            print key
            for item in value:
                self.__print_position(item)
    
    def __get_date_positions(self, date):
        pos = {}

        for item in self.positions:
            if date == item["start-date"]:
                pos.setdefault("open", []).append(item)
            elif date > item["start-date"]:
                if not item.get("close-date"):
                    pos.setdefault("hold", []).append(item)
                elif date < item["close-date"]:
                    pos.setdefault("hold", []).append(item)
                elif date == item["close-date"]:
                    pos.setdefault("sell", []).append(item)
        return pos

    def __update_perf(self, fund, perf, date):
        perf["equity"] = 0
        
        if fund.get("open"):
            for pos in fund["open"]:
                open_amt = pos["units"] * pos["start-price"]
                perf["equity"] += open_amt
            
                if perf["liquid"] < open_amt:
                    perf["invest"] += open_amt - perf["liquid"]
                    perf["liquid"] = 0
                else:
                    perf["liquid"] -= open_amt
        
        if fund.get("sell"):
            for pos in fund["sell"]:
                sell_amt = pos["units"] * pos["close-price"]
                perf["liquid"] += sell_amt

        if fund.get("hold"):
            for pos in fund["hold"]:
                hold_amt = pos["units"] * self.ticker.\
                    get_stock_price(date)
                perf["equity"] += hold_amt
        
        date_perf = {}
        date_perf["invest"] = perf["invest"]
        date_perf["liquid"] = perf["liquid"]
        date_perf["equity"] = perf["equity"]

        return date_perf

    def get_fund_perf(self):
        perf = {"invest": 0, "liquid": 0, "equity": 0}

        for date in self.dates:
            self.fund_hist[date] = self.__get_date_positions(date)
            self.perf_hist[date] = self.__update_perf(self.fund_hist[date],\
                perf, date)

    def print_perf_fund_history(self):
        for date in self.dates:
            self.ticker.print_stock_price(date)
            self.__print_fund(self.fund_hist[date])
            self.__print_perf(self.perf_hist[date])

    def __get_position_price_of_date(self, date, pos):

        if date == pos["start-date"]:
            price = pos["start-price"]
        elif pos.get("close-date") and date == pos["close-date"]:
            price = pos["close-price"]
        else:
            price = self.ticker.get_stock_price(date)

        return price

period = ["2010-01-01", "2015-11-20"]
spy_ticker = historical_stock_data("SPY")
spy_strategy = spy_strategy(spy_ticker, period)
perf = performance(spy_ticker)
perf.add_positions(spy_strategy.get_positions())
perf.get_fund_perf()
perf.print_perf_fund_history()

print "bench mark return"
print spy_ticker.calc_total_return(*period)
pprint (spy_ticker.calc_annual_return(*period))

#!/usr/bin/python
import re
import os
import pickle
from datetime import datetime
from pprint import pprint
from operator import itemgetter
from yahoo_finance import Share
from stock_data import historical_stock_data
from strategies import spy_strategies

class performance:
    def __init__(self):
        self.positions = []
        self.fund_hist = {}
        self.perf_hist = {}
        
    def add_positions(self, positions):
        self.positions.extend(positions)
        self.positions.sort(key=itemgetter('start-date'))

        for item in self.positions:
            self.__print_position(item)

        dates = self.positions[0]["ticker"].ticker.get_available_trading_dates()
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
                %(item["ticker"].ticker.name, \
                  item["type"], 
                  item["start-date"],
                  item["start-price"],
                  item["close-date"],
                  item["close-price"],
                  gain)
        else:
            today_date = datetime.today().strftime("%Y-%m-%d")
            today_price = item["ticker"].ticker.get_current_price_from_yahoo()
            gain = (today_price - item["start-price"]) \
                   / item["start-price"] * 100

            print "symbol:%s type:%s %s %f open:%s %f gain=%s" \
                %(item["ticker"].ticker.name, \
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
                hold_amt = pos["units"] * pos["ticker"].ticker.\
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
            fund = self.__get_date_positions(date)
            self.fund_hist[date] = fund
            perf = self.__update_perf(fund, perf, date)
            self.perf_hist[date] = perf

            print date
            self.__print_fund(fund)
            self.__print_perf(perf)

    def __print_fund(self, fund):
        if not fund:
            return

        for key, value in fund.iteritems():
            print key
            for item in value:
                self.__print_position(item)
    
    def __get_position_price_of_date(self, date, pos):

        if date == pos["start-date"]:
            price = pos["start-price"]
        elif pos.get("close-date") and date == pos["close-date"]:
            price = pos["close-price"]
        else:
            price = pos["ticker"].ticker.get_stock_price(date)

        return price

    # def __get_prev_date(self, date):
    #     prev_date = None

    #     if date in self.dates:
    #         idx_date = self.dates.index(date)

    #         if idx_date > 0:
    #             prev_date = self.dates[idx_date - 1]
    #         else:
    #             print "Fund start date %s" % date
    #     else:
    #         print "Error: no trading date: %s" % date

    #     return prev_date

period = ["2010-01-01", "2015-11-20"]
spy = spy_strategies('SPY', period)
perf = performance()
perf.add_positions(spy.get_positions())
perf.get_fund_perf()
spy.ticker.calc_annual_return(*period)

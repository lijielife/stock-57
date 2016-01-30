#!/usr/bin/env python

import os
import numpy as np
import pandas as pd
import pandas_datareader.data as pr
import datetime as dt
import argparse as ap

class stock_price:
    def __init__(self, ticker, data_dir):
        self.default_start = dt.datetime(1950, 1, 1)
        self.ticker = ticker
        self.price = pr.DataReader(ticker, "yahoo", start=self.default_start)

def get_cmd_line():
    parser = ap.ArgumentParser(description='update stock price')
    parser.add_argument("stock_symbol")
    parser.add_argument("data_dir")
    cmd_args = parser.parse_args()
    data_dir = os.path.abspath(cmd_args.data_dir)
    if not os.path.exists(data_dir):
        print "%s does not exist!" % src_dir
        sys.exit()

    return [cmd_args.stock_symbol, data_dir]

def main():
    cmd_line = get_cmd_line()

if __name__ == "__main__":
    main()

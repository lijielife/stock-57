#!/usr/bin/env python

import os
import numpy as np
import pandas as pd
import pandas_datareader.data as pr
import datetime as dt
import argparse as ap

class stock_data:
    def __init__(self, ticker):
        self.default_start = dt.datetime(1950, 1, 1)
        self.ticker = ticker
        self.price = pr.DataReader(ticker, "yahoo", start=self.default_start)

def get_data_dir():
    parser = ap.ArgumentParser(description='Get stock price')
    parser.add_argument("data_dir")
    cmd_args = parser.parse_args()
    data_dir = os.path.abspath(cmd_args.data_dir)
    if not os.path.exists(data_dir):
        print "%s does not exist!" % src_dir
        sys.exit()

    return data_dir

def main():
    data_dir = get_data_dir()
    print data_dir
    stock_data("QCOM")

if __name__ == "__main__":
    main()

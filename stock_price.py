#!/usr/bin/env python

import os
import numpy as np
import pandas as pd
import pandas_datareader.data as pr
import datetime as dt
import argparse as ap
import tables as tb


default_start = dt.datetime(1950, 1, 1)
default_url = 'yahoo'
default_file = 'stock_data.h5'

class stock_price:
    def __init__(self, ticker):
        # build stock price in pytable
        self.ticker = ticker

    def store_data(self, data_file):
        st = pd.HDFStore(data_file)
        st_node_dir = '/price/' + self.ticker

        node = st.get_storer(st_node_dir)
        if node == None:
            start = default_start
        else:
            nrows = node.table.nrows
            if nrows > 0:
                start = st.select(st_node_dir, where=[nrows - 1],
                                 columns=['Date']).index[0]
            else:
                start = default_start

        print start

        diff = dt.datetime.today() - start
        if diff.days > 1:
            price = pr.DataReader(self.ticker, "yahoo", start=start)
            st.append(st_node_dir, price)
        else:
            print "%s is already updated!" % self.ticker

        st.close()

def get_cmd_line():
    parser = ap.ArgumentParser(description='update stock price')
    parser.add_argument("stock_symbol")
    parser.add_argument("data_dir")
    cmd_args = parser.parse_args()
    data_dir = os.path.abspath(cmd_args.data_dir)
    if not os.path.exists(data_dir):
        print "%s does not exist!" % data_dir
        sys.exit()

    return [cmd_args.stock_symbol, data_dir]

def main():
    cmd_line = get_cmd_line()
    symbol = cmd_line[0]
    folder = cmd_line[1]
    stfile = folder + '/' + default_file
    price = stock_price(symbol)
    print stfile
    price.store_data(stfile)
    
if __name__ == "__main__":
    main()

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
default_file = 'prices.h5'

def download_price_yahoo(symbols, data_dir):
    map(lambda x: dr_yahoo(x, data_dir), symbols)

def dr_yahoo(symbol, data_dir):
    st = pd.HDFStore(os.path.join(data_dir, default_file))
    st_node_dir = '/price/' + symbol
    node = st.get_storer(st_node_dir)
    start = default_start

    if node:
        nrows = node.table.nrows
        if nrows:
            start = st.select(st_node_dir, where=[nrows - 1],
                    columns=['Date']).index[0]

    diff = dt.datetime.today() - start
    if diff.days > 1:
        print "%s from [%s] -> today" % (symbol, start)
        price = pr.DataReader(symbol, "yahoo", start=start)
        st.append(st_node_dir, price)
    else:
        print "%s is already updated!" % symbol

    st.close()

def get_cmd_line():
    parser = ap.ArgumentParser(description='update stock price')
    parser.add_argument("data_dir")
    cmd_args = parser.parse_args()
    data_dir = os.path.abspath(cmd_args.data_dir)
    if not os.path.exists(data_dir):
        print "%s does not exist!" % data_dir
        sys.exit()

    return  data_dir

def main():
    data_dir = get_cmd_line()
    symbols = ['QCOM', 'INTC', 'SWKS']
    price = download_price_yahoo(symbols, data_dir)
    
if __name__ == "__main__":
    main()

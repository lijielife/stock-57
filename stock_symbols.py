#!/usr/bin/env python

import os
import argparse as ap
import wget
import pandas as pd


def download_symbols(data_dir):
    url = ('http://www.nasdaq.com/screening/companies-by-industry.aspx?'
           'exchange=%s&render=download')
    markets = ['NYSE', 'NASDAQ', 'AMEX']
    csv_files = [wget.download((url % x), out=data_dir + '/' + x + '.csv')
                for x in markets]
    print 'symbols downloaded'

    return csv_files

def read_symbols(csv_files):
    frames = [pd.read_csv(x) for x in csv_files]
    symbols = pd.concat(frames)
    symbols.drop(['LastSale','MarketCap','ADR TSO', 'Summary Quote',
                  'Unnamed: 9'], axis=1, inplace=True)
    symbols.sort_values(by=['Sector', 'Industry', 'Symbol'],
                        inplace=True)
    symbols.index=range(0, len(symbols))

    return symbols

def store_symbols(data_dir, symbols):
    store = pd.HDFStore(data_dir + '/symbols.h5')

    symbol_node = '/symbols'
    if store.get_storer(symbol_node) == None:
        store.append(symbol_node, symbols, data_columns=True)
    else:
        print '/symbols exists'

    sector_node = '/sectors'
    if store.get_storer(sector_node) == None:
        sectors = symbols[['Sector', 'Industry']].drop_duplicates(keep='last')
        sectors.index=range(0, len(sectors))
        store.append(sector_node, sectors, data_columns=True)
    else:
        print '/sectors exists'

    store.close()

def get_cmd_line():
    parser = ap.ArgumentParser(description='update stock symbols')
    parser.add_argument("data_dir")
    cmd_args = parser.parse_args()
    data_dir = os.path.abspath(cmd_args.data_dir)
    if not os.path.exists(data_dir):
        print "%s does not exist!" % data_dir
        os.sys.exit()

    return data_dir

def main():
    data_dir = get_cmd_line()
    csv_files = download_symbols(data_dir)
    symbols = read_symbols(csv_files)
    store_symbols(data_dir, symbols)

if __name__ == "__main__":
    main()


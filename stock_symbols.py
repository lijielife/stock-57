#!/usr/bin/env python

import os
import argparse as ap
import wget
import pandas as pd
import datetime as dt

symbol_file = 'symbols.h5'
data_dir = '/home/yangh/ws/stock-data/'

def select_symbols(sector, industry):
    store = pd.HDFStore(os.path.join(data_dir, symbol_file))
    symbols = store['/symbols']
    sel = symbols[(symbols['Sector'] == sector) & (symbols['Industry'] ==
            industry)]

    return sel

def download_symbols(data_dir):
    url = ('http://www.nasdaq.com/screening/companies-by-industry.aspx?'
           'exchange=%s&render=download')
    markets = ['NYSE', 'NASDAQ', 'AMEX']
    csv_files = [wget.download((url % x), out=data_dir + '/' + x + '.csv')
                for x in markets]
    print ''
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

def log_symbols(symbols, s_old):
    t_str = dt.datetime.today().strftime("%Y-%m-%d")
    log_a = symbols[~symbols['Symbol'].isin(s_old['Symbol'])][['Symbol',
                                                               'Name']]
    log_a['Change'] = 'A'
    log_a['Date'] = t_str

    log_d = s_old[~s_old['Symbol'].isin(symbols['Symbol'])][['Symbol', 'Name']]
    log_d['Change'] = 'D'
    log_d['Date'] = t_str

    return pd.concat([log_a, log_d])

def store_symbols(store, symbols):
    if store.get_storer('/symbols') != None:
        s_old = store['/symbols']
        log = log_symbols(symbols, s_old)
        print log
        store.append('/log', log, data_columns=True)
    store.put('/symbols', symbols, table=True)

    sectors = symbols[['Sector', 'Industry']].drop_duplicates(keep='last')
    sectors.index=range(0, len(sectors))
    store.put('/sectors', sectors, table=True)

def update_symbols(data_dir):
    csv_files = download_symbols(data_dir)
    symbols = read_symbols(csv_files)
    store = pd.HDFStore(os.path.join(data_dir + symbol_file))
    store_symbols(store, symbols)
    store.close()
    map(os.remove, csv_files)

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
    update_symbols(data_dir)

if __name__ == "__main__":
    main()


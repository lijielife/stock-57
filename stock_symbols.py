#!/usr/bin/env python

import os
import argparse as ap
import wget

def download_symbols(data_dir):
    url = ('http://www.nasdaq.com/screening/companies-by-industry.aspx?'
            'exchange=%s&render=download')
    markets = ['NYSE', 'NASDAQ', 'AMEX']

    csvs = [wget.download((url % x), out=data_dir + '/' + x + '.csv')
                for x in markets]

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
    download_symbols(data_dir)

if __name__ == "__main__":
    main()


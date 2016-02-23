#!/usr/bin/env python

import os
import re
import argparse as ap
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from retrying import retry

profile_folder = '/home/yangh/.mozilla/firefox/webdriver-profile'

url_morningstar = ('http://financials.morningstar.com/%s.html?'
                   't=%s&region=USA&culture=en_US')

url_statement = {
    'income': 'income-statement/is',
    'balance_sheet': 'balance-sheet/bs',
    'cash_flow': 'cash-flow/cf',
    'ratio': 'ratios/r'
}


csv_filename = {
    'income': 'Income Statement',
    'balance_sheet': 'Balance Sheet',
    'cash_flow': 'Cash Flow',
    'ratio': 'Key Ratios'
}

freq = ['Quarterly', 'Annual']
prefix = 'Y'

def start_firefox_webdriver(profile_folder):
    profile = webdriver.FirefoxProfile(profile_folder)
    driver = webdriver.Firefox(firefox_profile=profile)
    return driver

@retry(wait_fixed=200, stop_max_delay=10000)
def read_csv(csv, skip):
    return pd.read_csv(csv, skiprows=skip)

def download_statement_settings(driver, freq):
    if freq == 'Quarterly':
        driver.execute_script("SRT_stocFund.ChangeFreq(3,'Quarterly')")
    elif freq == 'Annual':
        driver.execute_script("SRT_stocFund.ChangeFreq(12,'Annual')")
    driver.execute_script("SRT_stocFund.orderControl('asc','Ascending')")
    driver.execute_script("SRT_stocFund.ChangeRounding(-1)") # in thousand
    driver.execute_script("SRT_stocFund.changeDataType('R','Restated')")
    driver.execute_script("SRT_stocFund.Export()")

def download_keyratios_settings(driver):
    driver.execute_script("orderChange('asc','Ascending')")
    driver.execute_script("exportKeyStat2CSV()")

# keys cannot be only numbers or have '-', so rename column keys with
# Yxxxxx-xx
def rename_columns(statement):
    cols = statement.columns.tolist()
    cols[0] = 'report'

    statement.columns = [re.sub(r'^([0-9].+)-([0-9].+$)',
           prefix + r'\1'+'_'+r'\2', x) for x in cols]

    return statement

def rename_columns_back(statement):
    cols = statement.columns.tolist()
    statement.columns = [re.sub(r'^Y([0-9].+)_([0-9].+$)',
           r'\1'+'-'+r'\2', x) for x in cols]
    return statement

def store_statement(store, h5_node, statement):
    if store.get_storer(h5_node) == None:
        store.append(h5_node, statement, data_columns=True)
    else:
        # python set is good to find the diff
        s_orig = store[h5_node]
        s_diff = list(set(statement.columns.tolist()) -
                      set(s_orig.columns.tolist()))
        if s_diff:
            s_orig[s_diff] = statement[s_diff]
            if 'TTM' in statement:
                s_orig['TTM'] = statement['TTM']
            store.put(h5_node, s_orig, table=True)
            print "update database"
        else:
            print "no update"

def keyratios_data(driver, csv, store, node):
    print csv
    download_keyratios_settings(driver)
    statement = rename_columns(read_csv(csv, 2))
    store_statement(store, node, statement)
    os.remove(csv)

def statement_data(driver, f, csv, store, node):
    print csv + ' ' + f
    download_statement_settings(driver, f)
    statement = rename_columns(read_csv(csv, 1))
    st_node = node + '/' + f
    store_statement(store, st_node, statement)
    os.remove(csv)

def download_single_statement(symbol, driver, data_dir, store, st_type):
    csv = os.path.join(data_dir, '%s %s.csv' %(symbol, csv_filename[st_type]))
    url = url_morningstar % (url_statement[st_type], symbol)
    node = '/%s/%s' %(symbol, st_type)
    driver.get(url)

    if st_type == 'ratio':
        keyratios_data(driver, csv, store, node)
    else:
        map(lambda f: statement_data(driver, f, csv, store, node), freq)

def download_financial(symbol, driver, data_dir):
    store = pd.HDFStore(data_dir + '/financials.h5')
    print symbol + ' downloading...'

    map(lambda x: download_single_statement(symbol, driver, data_dir, store, x), 
        csv_filename.keys())

    store.close()

def start_download(symbols, data_dir):
    driver = start_firefox_webdriver(profile_folder)
    map(lambda x: download_financial(x, driver, data_dir), symbols)

def get_cmd_line():
    parser = ap.ArgumentParser(description='update stock financial data')
    parser.add_argument("data_dir")
    cmd_args = parser.parse_args()
    data_dir = os.path.abspath(cmd_args.data_dir)
    if not os.path.exists(data_dir):
        print "%s does not exist!" % data_dir
        os.sys.exit()

    return data_dir

def main():
    data_dir = get_cmd_line()
    symbols = ['QCOM', 'SWKS', 'INTC']
    start_download(symbols, data_dir)

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import os
import argparse as ap
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from retrying import retry

profile_folder = '/home/yangh/.mozilla/firefox/webdriver-profile'
def start_firefox_webdriver():
    profile = webdriver.FirefoxProfile(profile_folder)
    driver = webdriver.Firefox(firefox_profile=profile)
    
    return driver

abbrev_statement = {
    'Revenue': 'revenue',
    'Cost of revenue': 'cost',
    'Gross profit': 'profit',
    'Research and development': 'RD',
    'Sales, General and administrative': 'SGA',
    'Other operating expenses': 'op_expense_other',
    'Total operating expenses': 'op_expense_total',
    'Operating income': 'op_income',
    'Interest Expense': 'expense_int',
    'Other income (expense)': 'income_other',
    'Income before taxes': 'income_before_tax',
    'Provision for income taxes': 'taxes',
    'Net income from continuing operations': 'net_income_ops',
    'Net income from discontinuing ops': 'net_income_dis_ops',
    'Other': 'net_income_other',
    'Net income': 'net_income',
    'Net income available to common shareholders': 'net_income_common',
    'Earnings per share Basic': 'earnings_basic',
    'Earnings per share Diluted': 'earnings_diluted',
    'Weighted average shares outstanding Basic': 'shares_basic',
    'Weighted average shares outstanding Diluted': 'shares_diluted',
    'EBITDA': 'ebitda'
}

def abbrev_income(column_list):
    print column_list

def transpose_statement(statement):
    cols = statement.columns.tolist()
    cols[0] = 'quarter'
    statement.columns = cols
    statement.set_index('quarter', inplace=True)

    return statement.transpose()

# Remove 'Operating expenses' since no data in it
# Merge below 3 items
# 'Earnings per share'
# 'Basic'
# 'Diluted'
# to:
# 'Earnings per share Basic'
# 'Earnings per share Diluted'
# Merge below 3 items
# 'Weighted average shares outstanding
# 'Basic'
# 'Diluted'
# to:
# 'Weighted average shares outstanding Basic': 'shares_basic',
# 'Weighted average shares outstanding Diluted': 'shares_diluted',

def merge_income_items(income):
    cols = income.columns.tolist()

    idx = cols.index('Operating expenses')
    cols.pop(idx)

    idx = cols.index('Earnings per share')
    cols.pop(idx)
    cols[idx] = 'Earnings per share Basic'
    cols[idx + 1] = 'Earnings per share Diluted'

    idx = cols.index('Weighted average shares outstanding')
    cols.pop(idx)
    cols[idx] = 'Weighted average shares outstanding Basic'
    cols[idx + 1] = 'Weighted average shares outstanding Diluted'

    income.drop(['Operating expenses',
                 'Earnings per share',
                 'Weighted average shares outstanding',
                 ], axis=1, inplace=True)

    income.columns = [abbrev_statement[x] for x in cols]

def download_financial_morningstar(symbol, driver, store, data_dir):

    # Income statement
    url = ('http://financials.morningstar.com/income-statement/is.html?'
           't=%s&region=USA&culture=en_US') % symbol

    is_csv = os.path.join(data_dir, '%s Income Statement.csv' %symbol)

    driver.get(url)
    driver.execute_script("SRT_stocFund.orderControl('asc','Ascending')")
    # in thousands
    driver.execute_script("SRT_stocFund.ChangeRounding(-1)")
    driver.execute_script("SRT_stocFund.changeDataType('R','Restated')")
    # download quarterly data
    driver.execute_script("SRT_stocFund.ChangeFreq(3,'Quarterly')")
    driver.execute_script("SRT_stocFund.Export()")

    @retry(wait_fixed=200, stop_max_delay=10000)
    def read_csv(is_csv):
        return pd.read_csv(is_csv, skiprows=1)

    income = transpose_statement(read_csv(is_csv))

    merge_income_items(income)

    income_node = '/quarterly/income/' + symbol
    if store.get_storer(income_node) == None:
        store.append(income_node, income, data_columns=True)

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
    driver = start_firefox_webdriver()
    store = pd.HDFStore(data_dir + '/financials.h5')
    download_financial_morningstar('QCOM', driver, store, data_dir)
    store.close()
if __name__ == "__main__":
    main()



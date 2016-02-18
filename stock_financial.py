#!/usr/bin/env python

import os
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
    'cash_flow': 'cash-flow/cf'
}

csv_filename = {
    'income': 'Income Statement',
    'balance_sheet': 'Balance Sheet',
    'cash_flow': 'Cash Flow'
}

freq = ['Quarterly', 'Annual']

abbrev_income = {
    'Revenue': 'revenue',
    'Cost of revenue': 'cost',
    'Gross profit': 'profit',
    'Research and development': 'RD',
    'Sales, General and administrative': 'SGA',
    'Restructuring, merger and acquisition': 'RMA',
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

abbrev_balance_sheet = {
    'Cash and cash equivalents': 'cash',
    'Short-term investments': 'investments_st',
    'Total cash': 'cash_total',
    'Receivables': 'receivables',
    'Inventories': 'inventories',
    'Current assets Deferred income taxes': 'taxes_cur',
    'Other current assets': 'assets_cur_other',
    'Total current assets': 'assets_cur_total',
    'Gross property, plant and equipment': 'gross_ppe',
    'Accumulated Depreciation': 'acc_depre',
    'Net property, plant and equipment': 'net_ppe',
    'Equity and other investments': 'equity',
    'Goodwill': 'goodwill',
    'Intangible assets': 'intangible',
    'Non-current assets Deferred income taxes': 'taxes_non_cur',
    'Other long-term assets': 'assets_lt_other',
    'Total non-current assets': 'assets_non_cur_total',
    'Total assets': 'assets_total',
    'Short-term debt': 'debt_st',
    'Accounts payable': 'accounts_payable',
    'Accrued liabilities': 'liabilities_accrued',
    'Current liabilities Deferred revenues': 'revenue_cur_lia_deferred',
    'Other current liabilities': 'liabilities_cur_other',
    'Total current liabilities': 'liabilities_cur_total',
    'Long-term debt': 'debt_lt',
    'Non-current liabilities Deferred revenues': 'revenues_non_cur_lia_deferred',
    'Minority interest': 'interest_minority',
    'Deferred taxes liabilities': 'liabilities_deferred_taxes',
    'Other long-term liabilities': 'liabilities_lt_other',
    'Total non-current liabilities': 'liabilities_non_cur_total',
    'Total liabilities': 'liabilities_total',
    'Common stock': 'common_stock',
    'Additional paid-in capital': 'apic',
    'Retained earnings': 'returned_earnings',
    'Treasury stock': 'treasury_stock',
    'Accumulated other comprehensive income': 'income_aoc',
    "Total stockholders' equity": 'equity_total',
    "Total liabilities and stockholders' equity": 'liabilities_equity_total'
}

abbrev_cash_flow = {
    'Net income': 'net_income',
    'Depreciation & amortization': 'depreciation_amortization',
    'Investment/asset impairment charges': 'impairment_charge',
    'Investments losses (gains)': 'investment_gains',
    'Deferred income taxes': 'taxes_deferred',
    'Stock based compensation': 'stock_comp',
    'Accounts receivable': 'accounts_receivable',
    'Inventory': 'inventory',
    'Accounts payable': 'accounts_payable',
    'Accrued liabilities': 'liabilities_accrued',
    'Income taxes payable': 'taxes_payable',
    'Other working capital': 'working_cap_other',
    'Other non-cash items': 'non_cash_other',
    'Net cash provided by operating activities': 'net_cash_op',
    'Investments in property, plant, and equipment': 'ppe_investment',
    'Property, plant, and equipment reductions': 'ppe_reduction',
    'Acquisitions, net': 'acquisitions_net',
    'Purchases of investments': 'investments_purchases',
    'Sales/Maturities of investments': 'investments_sales',
    'Purchases of intangibles': 'purchases_intangible',
    'Sales of intangibles': 'sales_intangible',
    'Sales of intangible': 'sales_intangible',
    'Other investing activities': 'investment_other',
    'Net cash used for investing activities': 'investment_cash',
    'Debt issued': 'debt_issued',
    'Debt repayment': 'debt_repayment',
    'Common stock issued': 'stock_issued',
    'Common stock repurchased': 'stock_repurchased',
    'Excess tax benefit from stock based compensation': 'tax_benefit_stock_comp',
    'Dividend paid': 'dividend_paid',
    'Other financing activities': 'financing_other',
    'Net cash provided by (used for) financing activities': 'net_cash_financing',
    'Effect of exchange rate changes': 'effect_exchange_rate',
    'Net change in cash': 'net_change',
    'Cash at beginning of period': 'cash_beginning',
    'Cash at end of period': 'cash_end',
    'Operating cash flow': 'cash_flow_op',
    'Capital expenditure': 'cap_exp',
    'Free cash flow': 'free_cash_flow'
}

def start_firefox_webdriver(profile_folder):
    profile = webdriver.FirefoxProfile(profile_folder)
    driver = webdriver.Firefox(firefox_profile=profile)

    return driver

@retry(wait_fixed=200, stop_max_delay=10000)
def read_csv(csv):
    return pd.read_csv(csv, skiprows=1)

def transpose_statement(statement):
    cols = statement.columns.tolist()
    cols[0] = 'report'
    statement.columns = cols
    statement.set_index('report', inplace=True)

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

def merge_items_income(income):
    cols = income.columns.tolist()

    if 'Operating expenses' in cols:
        idx = cols.index('Operating expenses')
        cols.pop(idx)

    if 'Earnings per share' in cols:
        idx = cols.index('Earnings per share')
        cols.pop(idx)
        cols[idx] = 'Earnings per share Basic'
        cols[idx + 1] = 'Earnings per share Diluted'

    if 'Weighted average shares outstanding' in cols:
        idx = cols.index('Weighted average shares outstanding')
        cols.pop(idx)
        cols[idx] = 'Weighted average shares outstanding Basic'
        cols[idx + 1] = 'Weighted average shares outstanding Diluted'

    income.drop(['Operating expenses',
                 'Earnings per share',
                 'Weighted average shares outstanding',
                 'TTM'
                 ], axis=1, inplace=True)

    income.columns = [abbrev_income.get(x) if abbrev_income.get(x)
                      else x for x in cols]

def merge_items_balance_sheet(bs):
    bs.drop(['Assets', 'Current assets', 'Cash',
             'Property, plant and equipment', 'Non-current assets',
             "Liabilities and stockholders\' equity", 'Liabilities',
             'Current liabilities', 'Non-current liabilities',
             "Stockholders\' equity"], axis=1, inplace=True)

    cols = bs.columns.tolist()

    if 'Deferred income taxes' in cols:
        idx = cols.index('Deferred income taxes')
        cols[idx] = 'Current assets Deferred income taxes'

    if 'Deferred income taxes' in cols:
        idx = cols.index('Deferred income taxes')
        cols[idx] = 'Non-current assets Deferred income taxes'

    if 'Deferred revenues' in cols:
        idx = cols.index('Deferred revenues')
        cols[idx] = 'Current liabilities Deferred revenues'

    if 'Deferred revenues' in cols:
        idx = cols.index('Deferred revenues')
        cols[idx] = 'Non-current liabilities Deferred revenues'

    bs.columns = [abbrev_balance_sheet.get(x)
                  if abbrev_balance_sheet.get(x) else x for x in cols]

def merge_items_cash_flow(cf):
    cf.drop(['Cash Flows From Operating Activities',
             'Cash Flows From Investing Activities',
             'Cash Flows From Financing Activities',
             'Free Cash Flow'], axis=1, inplace=True)
    cols = cf.columns.tolist()
    cf.columns = [abbrev_cash_flow.get(x)
                  if abbrev_cash_flow.get(x) else x for x in cols]


def download_statement(driver, freq):
    if freq == 'Quarterly':
        driver.execute_script("SRT_stocFund.ChangeFreq(3,'Quarterly')")
    elif freq == 'Annual':
        driver.execute_script("SRT_stocFund.ChangeFreq(12,'Annual')")
    driver.execute_script("SRT_stocFund.orderControl('asc','Ascending')")
    driver.execute_script("SRT_stocFund.ChangeRounding(-1)") # in thousand
    driver.execute_script("SRT_stocFund.changeDataType('R','Restated')")
    driver.execute_script("SRT_stocFund.Export()")

def store_statement(st_type, csv, store, h5_node):
    statement = transpose_statement(read_csv(csv))
    os.remove(csv)

    if st_type == 'income':
        merge_items_income(statement)
    elif st_type == 'balance_sheet':
        merge_items_balance_sheet(statement)
    elif st_type == 'cash_flow':
        merge_items_cash_flow(statement)

    if store.get_storer(h5_node) == None:
        store.append(h5_node, statement, data_columns=True)

def download_financial_morningstar(symbol, st_type, driver, url, store, csv):
    driver.get(url)
    for f in freq:
        download_statement(driver, f)
        h5_node = '/' + st_type + '/' + f + '/' + symbol
        store_statement(st_type, csv, store, h5_node)

def download_symbol_financial(symbol, driver, data_dir):
    store = pd.HDFStore(data_dir + '/financials.h5')
    print symbol + ' downloading...'

    for st_type in csv_filename.keys():
        print symbol + '->' + csv_filename[st_type]
        csv = os.path.join(data_dir,
                           '%s %s.csv' %(symbol, csv_filename[st_type]))
        url = url_morningstar %(url_statement[st_type], symbol)
        download_financial_morningstar(symbol, st_type, driver, url, store, csv)

    store.close()

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
    symbol = ['QCOM', 'SWKS', 'INTC']
    driver = start_firefox_webdriver(profile_folder)
    map(lambda x: download_symbol_financial(x, driver, data_dir), symbol)

if __name__ == "__main__":
    main()

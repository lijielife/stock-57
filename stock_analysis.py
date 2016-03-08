#!/usr/bin/env python

import os
import locale
import pandas as pd
import matplotlib.pyplot as plt
from stock_symbols import pick_symbols
from stock_financial import rename_columns_back

file_price = '/home/yangh/ws/stock-data/prices.h5'
file_financial = '/home/yangh/ws/stock-data/financials.h5'

locale.setlocale(locale.LC_NUMERIC, '')

sel = pick_symbols()

nodes = ['/%s/ratio', '/%s/income/Annual', '/%s/income/Quarterly',
         '/%s/balance_sheet/Quarterly', '/%s/balance_sheet/Annual',
         '/%s/cash_flow/Quarterly', '/%s/cash_flow/Annual']

def set_color(df):
    return ['r' if x < 0 else 'b' for x in df]

def get_price_data(symbol):
    store = pd.HDFStore(file_price)
    node = '/price/%s' %symbol
    return store[node]['Adj Close']

def get_financial_data(node):
    store = pd.HDFStore(file_financial)
    data = store[node]
    rename_columns_back(data)
    data.set_index('report', inplace=True)
    return data
    
def plot_data_and_change(symbol, data, title):
    chg = data / data.shift(1) - 1

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12,4))

    data.plot(ax=axes[0], kind='bar', color=set_color(data),
              title="%s %s" %(symbol, title))
    chg.plot(ax=axes[1], kind='bar', color=set_color(chg),
             title='%s %s change' %(symbol, title))

def plot_item(symbol, title, y_data, q_data):
    plot_data_and_change(symbol, y_data[title], title)
    plot_data_and_change(symbol, q_data[title], title)

def get_income_annual(financials):
    y_income = pd.DataFrame()
    y_income['revenue'] = financials[0].loc['Revenue USD Mil'].apply(locale.atof);

    gross_margin = financials[0].loc['Gross Margin %'].apply(locale.atof) / 100.0
    y_income['gross_profit'] = y_income['revenue'] * gross_margin
    y_income['gross_margin'] = gross_margin

    y_income['op_income'] = financials[0].loc['Operating Income USD Mil'].\
                apply(locale.atof)
    y_income['op_margin'] = y_income['op_income'] / y_income['revenue']

    y_income['net_income'] = financials[0].loc['Net Income USD Mil'].\
                apply(locale.atof)
    y_income['net_margin'] = y_income['net_income'] / y_income['revenue']

    y_income['cash_flow'] = financials[0].loc['Operating Cash Flow USD Mil'].\
                apply(locale.atof)
    y_income['cash_flow_margin'] = y_income['cash_flow'] / y_income['revenue']

    y_income['free_cash_flow'] = financials[0].loc['Free Cash Flow USD Mil'].\
                apply(locale.atof)
    y_income['free_cash_margin'] = y_income['free_cash_flow'] / y_income['revenue']

    return y_income

def get_income_quarterly(financials):
    q_income = pd.DataFrame()
    q_income['revenue'] = financials[2].loc['Revenue']

    q_income['gross_profit'] = financials[2].loc['Gross profit']
    q_income['gross_margin'] = q_income['gross_profit'] / q_income['revenue']

    q_income['op_income'] = financials[2].loc['Operating income']
    q_income['op_margin'] = q_income['op_income'] / q_income['revenue']

    q_income['net_income'] = financials[2].loc['Net income']
    q_income['net_margin'] = q_income['net_income'] / q_income['revenue']

    q_income['cash_flow'] = financials[5].loc['Operating cash flow']
    q_income['cash_flow_margin'] = q_income['cash_flow'] / q_income['revenue']

    q_income['free_cash_flow'] = financials[5].loc['Free cash flow']
    q_income['free_cash_margin'] = q_income['free_cash_flow'] /\
            q_income['revenue']

    return q_income

def get_balance_anual(financials):
    y_balance = pd.DataFrame()
    y_balance['cash_value'] = financials[4].loc['Total cash']
    y_balance['long_term_debt'] = financials[4].\
            loc['Total non-current liabilities']
    y_balance['net_cash_value'] = y_balance['cash_value'] - \
            y_balance['long_term_debt']

    y_balance['net_cash_per_share'] = y_balance['net_cash_value'] /\
            financials[1].loc['Basic'].iloc[1]

    return y_balance

def get_balance_quarterly(financials):
    q_balance = pd.DataFrame()
    q_balance['cash_value'] = financials[3].loc['Total cash']
    q_balance['long_term_debt'] = financials[3].\
            loc['Total non-current liabilities']
    q_balance['net_cash_value'] = q_balance['cash_value'] - \
            q_balance['long_term_debt']

    q_balance['net_cash_per_share'] = q_balance['net_cash_value'] /\
            financials[2].loc['Basic'].iloc[1]

    return q_balance

def plot_financials(symbol):
    price = get_price_data(symbol)
    financials = [get_financial_data(x % symbol) for x in nodes]

    plt.figure()
    price['2006-12-01'::].plot(grid=True, figsize=(12,4), title=symbol)

    y_in = get_income_annual(financials)
    q_in = get_income_quarterly(financials)

    y_bs = get_balance_anual(financials)
    q_bs = get_balance_quarterly(financials)

    item = ['revenue', 'op_income', 'op_margin', 'net_income', 'cash_flow',
            'free_cash_flow']

    map(lambda x: plot_item(symbol, x, y_in, q_in), item)

    item = ['net_cash_value', 'net_cash_per_share']
    map(lambda x: plot_item(symbol, x, y_bs, q_bs), item)

map(lambda x: plot_financials(x), sel['Symbol'])

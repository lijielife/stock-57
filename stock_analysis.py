#!/usr/bin/env python

import os
import locale
import pandas as pd
import matplotlib.pyplot as plt
from stock_symbols import select_symbols
from stock_financial import rename_columns_back


file_price = '/home/yangh/ws/stock-data/prices.h5'
file_financial = '/home/yangh/ws/stock-data/financials.h5'

locale.setlocale(locale.LC_NUMERIC, '')

sel = select_symbols('Capital Goods', 'Electronic Components')
symbol = 'QCOM'

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
    
def plot_data_and_change(data, title):
    chg = data / data.shift(1) - 1

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12,4))

    data.plot(ax=axes[0], kind='bar', color=set_color(data), title=title)
    chg.plot(ax=axes[1], kind='bar', color=set_color(chg), title='change')


def get_revenue(financials):
    return [financials[0].loc['Revenue USD Mil'].apply(locale.atof),
            financials[2].loc['Revenue']]

def get_gross_profit(financials):
    return [financials[0].loc['Gross Margin %'].apply(locale.atof) *
            financials[0].loc['Revenue USD Mil'].apply(locale.atof),
            financials[2].loc['Gross profit']]

def get_gross_margin(financials):
    q_gross_margin = financials[2].loc['Gross profit'] /\
                     financials[2].loc['Revenue']

    return [financials[0].loc['Gross Margin %'].apply(locale.atof),
            q_gross_margin]

def get_op_income(financials):
    return [financials[0].loc['Operating Income USD Mil'].apply(locale.atof),
            financials[2].loc['Operating income']]

def get_op_margin(financials):
    q_op_margin = financials[2].loc['Operating income'] /\
                  financials[2].loc['Revenue']

    return [financials[0].loc['Operating Margin %'].apply(locale.atof),
            q_op_margin]

def plot_financials(symbol):
    price = get_price_data(symbol)
    financials = [get_financial_data(x % symbol) for x in nodes]

    plt.figure()
    price['2006-12-01'::].plot(grid=True, figsize=(12,4), title=symbol)

    map(lambda x: plot_data_and_change(x, 'revenue'), get_revenue(financials))
    map(lambda x: plot_data_and_change(x, 'gross_margin'),
            get_gross_margin(financials))
    map(lambda x: plot_data_and_change(x, 'op_income'),
            get_op_income(financials))
    map(lambda x: plot_data_and_change(x, 'op_margin'),
            get_op_margin(financials))

map(lambda x: plot_financials(x), sel['Symbol'])

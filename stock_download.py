#!/usr/bin/env python

import pandas as pd
from stock_financial import download_financial_morningstar
from stock_price import download_price_yahoo
from stock_symbols import pick_symbols

sel = pick_symbols()

download_financial_morningstar(sel['Symbol'], '/home/yangh/ws/stock-data')
download_price_yahoo(sel['Symbol'], '/home/yangh/ws/stock-data')

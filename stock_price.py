
import numpy as np
import pandas as pd
from pandas_datareader import data
import datetime

class stock_data:
    def __init__(self, ticker):
        self.default_start = datetime.datetime(1950, 1, 1)
        self.ticker = ticker
        self.price = data.DataReader(ticker, "yahoo", start=self.default_start)

stock_data("QCOM")

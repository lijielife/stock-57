#!/usr/bin/python

import numpy as np
import pandas as pd
import pandas.io.data as web


sp500 = web.DataReader("^GSPC", data_source="yahoo", start="2000-01-01",
        end="2015-12-09")

sp500.info()
sp500["42d"] = np.round(pd.rolling_mean(sp500["Close"], window=42), 2)
sp500["252d"] = np.round(pd.rolling_mean(sp500["Close"], window=252), 2)

sp500[["Close", "42d", "252d"]].plot(grid=True, figsize=(8, 5))

#!/usr/bin/python

import re


sp500_data = []


with open('sp500-history.csv') as file:
    sp500_data = file.readlines()


def find_sp500_month_data( sp500_data ):
    "reduce data set including only the last day of each month"

    sp500_data_month = []
    month_pre = 0
    
    for line in sp500_data:
        month = re.match( r'^(.*?)\/', line, re.M|re.I)
        if month :
            month_cur = int(month.group(1))
            if month_cur != month_pre:
                sp500_data_month.append(line)
                month_pre = month_cur

    return sp500_data_month;


sp500_m_d = find_sp500_month_data(sp500_data)
for num in range (1, len(sp500_m_d)):
    print sp500_m_d[-num].strip('\n')




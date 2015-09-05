#!/usr/bin/python

import re

sp500_data = []

with open('sp500-history.csv') as file:
    sp500_data = file.readlines()


def convert_csv_to_array( sp500_data ):
    "convert each line to arry with closing price"
    sp500_array = []
    
    for line in sp500_data:
        tmp = line.split(',')
        tmp[6] = tmp[6].rstrip('\r\n')
        tmp[6] = float(tmp[6])
        sp500_array.insert(0, [tmp[0], tmp[6]])

    return sp500_array

sp500_array = convert_csv_to_array(sp500_data)

# for tmp in sp500_array:
#     print tmp

def find_alltime_highs(sp500_array):
    "find sp500 all time highs"
    sp500_alltime_highs = []
    max = 0

    for i in range(0, (len(sp500_array) - 1)):
        cur = sp500_array[i][1]
        if cur > max:
            max = cur
            sp500_array[i].append(i)
            sp500_alltime_highs.append(sp500_array[i])

    return sp500_alltime_highs

sp500_alltime_highs = find_alltime_highs(sp500_array)

# for tmp in sp500_alltime_highs:
#     print tmp;

def linear_between_highs(sp500_array, sp500_alltime_highs):
    "find the lowest betwee 2 highs"
    for i in range (0, (len(sp500_alltime_highs) - 2)):
        
        min = sp500_alltime_highs[i];
        decrease_array = []
        
        print sp500_alltime_highs[i]
        print sp500_alltime_highs[i+1]

        for j in range(sp500_alltime_highs[i][2] + 1,
                       sp500_alltime_highs[i+1][2]):
            cur = sp500_array[j][1]
            if cur < min :
                 min = cur
                 decrease_array.append(sp500_array[j])
        
        
        print decrease_array
        print "====\n"



linear_between_highs(sp500_array, sp500_alltime_highs);

# sp500_m_d = find_sp500_month_data(sp500_data)

# for num in range (1, len(sp500_m_d)):
#     print sp500_m_d[-num].strip('\n')

# def find_sp500_month_data( sp500_data ):
#     "reduce data set including only the last day of each month"

#     sp500_data_month = []
#     month_pre = 0
    
#     for line in sp500_data:
#         month = re.match( r'^(.*?)\/', line, re.M|re.I)
#         if month :
#             month_cur = int(month.group(1))
#             if month_cur != month_pre:
#                 sp500_data_month.append(line)
#                 month_pre = month_cur

#     return sp500_data_month

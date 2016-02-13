#!/usr/bin/env python

import os
import argparse as ap
from selenium import webdriver


def download_financial_morningstar(symbol):
    # Income statement
    url = ('http://financials.morningstar.com/income-statement/is.html?'
           't=%s&region=USA&culture=en_US') % symbol

    driver = webdriver.Firefox()
    driver.get(url)

    driver.execute_script("SRT_stocFund.orderControl('asc','Ascending')")

    # in thousands
    driver.execute_script("SRT_stocFund.ChangeRounding(-1)")
    driver.execute_script("SRT_stocFund.changeDataType('A','As of Reported')")

    # download quarterly data
    driver.execute_script("SRT_stocFund.ChangeFreq(3,'Quarterly')")
    driver.execute_script("SRT_stocFund.Export()")

    # download annual data

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
    download_financial_morningstar('QCOM')

if __name__ == "__main__":
    main()



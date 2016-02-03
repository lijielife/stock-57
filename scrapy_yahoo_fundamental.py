#!/usr/bin/env python

import scrapy as sp
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import Compose, MapCompose, TakeFirst

import locale
from dateutil.parser import parse

class YahooFinancialSpider(sp.Spider):
    name = "yahoo-financial"
    allowed_domains = ["yahoo.com"]
    
    start_urls = ["http://finance.yahoo.com/q/is?s=QCOM"]
    
    def parse(self, response):
        l = FinancialItemLoader(item=FinancialItem(), response=response)
        print l.load_item()

class FinancialItem(sp.Item):
    symbol = Field()
    period = Field()
    total_revenue = Field()
    gross_profit = Field()
    ebit = Field()
    net_income = Field()

class FinancialItemLoader(ItemLoader):
    period_in = MapCompose(unicode.strip, parse)

    total_revenue_in = MapCompose(unicode.strip, locale.atoi)

    gross_profit_in = MapCompose(unicode.strip, locale.atoi)

    ebit_in = MapCompose(unicode.strip, locale.atoi)

    net_income_in = MapCompose(unicode.strip, locale.atoi)


    def __init__(self, *args, **kwargs):
        response = kwargs.get('response')
        item = kwargs.get('item')

        super(FinancialItemLoader, self).__init__(*args, **kwargs)

        xpath_period = (
            '//tr/td[./small/span'
            '[contains(., "Period Ending")]'
            ']/following-sibling::*/text()'
        )
        xpath_total_revenue = (
            '//tr/td[./strong'
            '[contains(., "Total Revenue")]'
            ']/following-sibling::*/strong/text()'
        )
        xpath_gross_profit = (
            '//tr/td[./strong'
            '[contains(., "Gross Profit")]'
            ']/following-sibling::*/strong/text()'
        )
        xpath_ebit = (
            '//tr/td'
            '[contains(., "Earnings Before Interest And Taxes")'
            ']/following-sibling::*/text()'
        )
        xpath_net_income = (
            '//tr/td[./strong'
            '[contains(., "Net Income Applicable To Common Shares")]'
            ']/following-sibling::*/strong/text()'
        )

        locale.setlocale(locale.LC_ALL, '')

        self.add_xpath('period', xpath_period)
        self.add_xpath('total_revenue', xpath_total_revenue)
        self.add_xpath('gross_profit', xpath_gross_profit)
        self.add_xpath('ebit', xpath_ebit)
        self.add_xpath('net_income', xpath_net_income)

def main():
     process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
     })
     process.crawl(YahooFinancialSpider)
     process.start()

if __name__ == "__main__":
    main()

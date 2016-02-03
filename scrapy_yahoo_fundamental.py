#!/usr/bin/env python

import scrapy as sp
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from scrapy.item import Item, Field

class YahooFinancialSpider(sp.Spider):
    name = "yahoo-financial"
    allowed_domains = ["yahoo.com"]
    
    start_urls = ["http://finance.yahoo.com/q/is?s=QCOM"]
    
    def parse(self, response):
        l = ItemLoader(item=FinancialItem(), response=response)
        l.add_xpath('date', '//tr/td[./small/span[contains(., "Period Ending")]]/following-sibling::*/text()')
        l.add_xpath('total_revenue', '//tr/td[./strong[contains(., "Total Revenue")]]/following-sibling::*/strong/text()')
        l.add_xpath('gross_profit', '//tr/td[./strong[contains(., "Gross Profit")]]/following-sibling::*/strong/text()')
        l.add_xpath('ebit', '//tr/td[contains(., "Earnings Before Interest And Taxes")]/following-sibling::*/text()')
        l.add_xpath('net_income', '//tr/td[./strong[contains(., "Net Income Applicable To Common Shares")]]/following-sibling::*/strong/text()')
        print l.load_item()

class FinancialItem(sp.Item):
    symbol = Field()
    date = Field()
    total_revenue = Field()
    gross_profit = Field()
    ebit = Field()
    net_income = Field()

def main():
     process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
     })
     process.crawl(YahooFinancialSpider)
     process.start()

if __name__ == "__main__":
    main()

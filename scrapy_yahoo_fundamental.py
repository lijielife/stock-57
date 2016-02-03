#!/usr/bin/env python

import scrapy as sp
from scrapy.crawler import CrawlerProcess


class YahooFinancialSpider(sp.Spider):
    name = "yahoo-financial"
    allowed_domains = ["yahoo.com"]
    
    start_urls = ["http://finance.yahoo.com/q/is?s=QCOM"]
    
    def parse(self, response):
         print response.xpath('//tr/td[./small/span[contains(., "Period Ending")]]/following-sibling::*/text()').extract()
         print response.xpath('//tr/td[./strong[contains(., "Total Revenue")]]/following-sibling::*/strong/text()').extract()
         print response.xpath('//tr/td[./strong[contains(., "Gross Profit")]]/following-sibling::*/strong/text()').extract()
         print response.xpath('//tr/td[contains(., "Earnings Before Interest And Taxes")]/following-sibling::*/text()').extract()
         print response.xpath('//tr/td[./strong[contains(., "Net Income Applicable To Common Shares")]]/following-sibling::*/strong/text()').extract()

def main():
     process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
     })
     process.crawl(YahooFinancialSpider)
     process.start()

if __name__ == "__main__":
    main()

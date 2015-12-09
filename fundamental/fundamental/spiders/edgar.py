import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.utils.response import open_in_browser
from pprint import pprint


class EdgarSpider(CrawlSpider):
    name = "edgar"
    allowed_domains = ["sec.gov"]
    start_urls = [
        ("http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=SWKS&"
         "type=10-&dateb=20151201&datea=20140101&owner=exclude&count=300")
        ]

    rules = (
        Rule(LinkExtractor(
                allow=('/Archives/edgar/data/[^\"]+\-index\.htm',))),
        Rule(LinkExtractor(
                allow=('/Archives/edgar/data/[^\"]+/[A-Za-z]+\-\d{8}\.xml',)),
             callback='parse_10qk')
        )

    def parse_10qk(self, response):
        print "parse_10qk"
        open_in_browser(response)

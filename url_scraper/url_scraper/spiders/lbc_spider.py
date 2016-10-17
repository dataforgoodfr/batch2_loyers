# -*- coding: utf-8 -*-
import scrapy


class LbcSpider(scrapy.Spider):
    name = "lbc_spider"
    allowed_domains = ["leboncoin.fr"]
    start_urls = (
        'http://www.leboncoin.fr/',
    )

    def parse(self, response):
        pass

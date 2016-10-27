# -*- coding: utf-8 -*-
import scrapy


class LogSpider(scrapy.Spider):
    name = "log_spider"
    allowed_domains = ["seloger.fr"]
    start_urls = (
        'http://www.seloger.fr/',
    )

    def parse(self, response):
        pass

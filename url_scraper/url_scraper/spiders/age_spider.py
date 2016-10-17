# -*- coding: utf-8 -*-
import scrapy


class AgeSpiderSpider(scrapy.Spider):

    def __init__(self, adress):
        name = "age_spider"
        allowed_domains = ["meilleursagents.com"]
        start_urls = (
            'http://www.meilleursagents.com/prix-immobilier/paris-75000/',
        )

    def parse(self, response, adress):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'q': adress},
            callback=self.after_search
        )

    def after_search(self, response):
        print 'ok'

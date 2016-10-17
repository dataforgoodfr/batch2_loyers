# -*- coding: utf-8 -*-

# This takes an url as argument and return a dict with the data on it.

import scrapy
from scrapy.crawler import CrawlerProcess
from url_scraper.spiders.pap_spider import PapSpider

url = 'http://www.pap.fr/annonce/locations-paris-75-g439-r413400026?u=1'
crawler = CrawlerProcess()
crawler.crawl(PapSpider, start_urls=[url])
crawler.start()

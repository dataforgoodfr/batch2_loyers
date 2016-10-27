# -*- coding: utf-8 -*-

# This takes an url as argument and return a dict with the data on it.

import scrapy, sys
from scrapy.crawler import CrawlerProcess
from url_scraper.spiders.pap_spider import PapSpider
from url_scraper.spiders.lbc_spider import LbcSpider
from url_scraper.spiders.log_spider import LogSpider
from argparse import ArgumentParser

def main(argv):

    # parse commandline argument
    parser = ArgumentParser()
    parser.add_argument('-url','--input',help='URL',type=str)
    url = parser.parse_args().input

    # get site from url
    if 'www.pap.fr' in url:
        spider = PapSpider
    elif 'www.seloger.com' in url:
        spider = LogSpider
    elif 'www.leboncoin.fr' in url:
        spider = LbcSpider
    else:
        parser.error('url cannot be parsed')
        sys.exit(-1)

    # run crawler
    crawler = CrawlerProcess()
    crawler.crawl(PapSpider, start_urls=[url])
    crawler.start()

if __name__ == '__main__':
    main(sys.argv)

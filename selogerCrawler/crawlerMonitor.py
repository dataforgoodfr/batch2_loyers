# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 23:34:24 2016

@author: aseghir
"""

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from spiders.selogerCrawler_spider import seLogerCrawlerSpider
from argparse import ArgumentParser
import sys


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
						PIPELINE					
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class SelogercrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
						SETTINGS					
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
settings = {
            'FEED_EXPORTERS': {'jsonlines': 'scrapy.contrib.exporter.JsonLinesItemExporter',},
            'FEED_FORMAT':'json',
            'FEED_URI':'OutputCrawl2.json',
            'ITEM_PIPELINES':{'__main__.SelogercrawlerPipeline':300},
            'DOWNLOAD_DELAY':2,
            'USER_AGENT':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
    }



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
						CRAWLER RUNNER					
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def runCrawler():
    configure_logging()
    global runner
    runner= CrawlerRunner()
    crawl()
    reactor.run() # the script will block here until the last crawl call is finished

cp=None

@defer.inlineCallbacks
def crawl():
    seLogerCrawlerSpider.custom_settings=settings
    yield runner.crawl(seLogerCrawlerSpider,cp=cp)
    reactor.stop()



def main(argv):
    global cp
    #================================Commande Line Parsing=========================================== 
    parser = ArgumentParser(description='SeLoger.com Crawler')
    parser.add_argument("-cp","--input",help="CODE POSTAL",type=int)
    parser.add_argument("-o","--output",help="RESULTS FILE PATH")

    args = parser.parse_args()

    if not(args.input):
        parser.error("POSTAL CODE IS MISSING")
        sys.exit(-1)
    if not (args.output):
        parser.error("JSON OUTPUT FILE PATH IS MISSING")
        sys.exit(-1)
    
    settings['FEED_URI']=str(args.output)
    cp=str(args.input)
    runCrawler()

#===================================Main call==============================================================
if __name__ == "__main__":
   main(sys.argv)
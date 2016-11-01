# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re, os, requests
import pandas as pd
from url_scraper.utils import get_sub_area

class PapScraperPipeline(object):

    def process_item(self, item, spider):

        def text_cleaner(text):
            # remove trailing \n and \r
            return re.sub("\n|\r", "", "".join(text))

        # parse price
        item['price'] = int(''.join(re.findall('\d+', item['price'])))

        # text cleaner
        item['text'] = text_cleaner(item['text'])
        item['title'] = text_cleaner(item['title'])

        # find sub_area from coord / text
        if item['coord']:
            words = item['adress'].split(',')
        else:
            words = item['text'].split()
        item['sub_area'] = get_sub_area(words)

        # area
        item['area'] = int(re.findall('\d+', item['area'])[0])

        # furnitures
        if 'meubl' in item['title']:
            item['furn'] = True
        else:
            item['furn'] = False

        # parse ref
        raw_ref = re.split(' / |:', item['ref_n'])
        item['ref_n'] = raw_ref[1]
        item['date'] = raw_ref[2].rstrip()

        # parse surface
        item['surface'] = int(re.findall('\d+', item['surface'])[0])

        return item

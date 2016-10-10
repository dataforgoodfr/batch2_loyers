# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re, os
import pandas as pd
from geopy.geocoders import Nominatim
from difflib import SequenceMatcher

class PapScraperPipeline(object):

    def __init__(self):
        self.path = os.path.realpath('..') + "\\data\\id_quartier.csv"
        self.sub_df = pd.read_csv(self.path)

    def similarity(self, a, b):
        # get string similarity ratio
        return SequenceMatcher(None, a, b).ratio()

    def get_sub_area(self, item):
        # try to extract sub_area from coord
        # else try with text data (takes more time)
        if item['coord']:
            geolocator = Nominatim()
            location = geolocator.reverse(item['coord'])
            words = location.address.split(',')
        else:
            words = item['text'].split()

        # compare the words in the adress / text to the list of areas
        max_length = max([len(i) for i in self.sub_df['L_QU']])
        words = [w for w in words if len(w) <= max_length]

        word_list = []
        for word in words:
            subs = self.sub_df[['OBJECTID', 'L_QU']].copy()
            subs['word'] = word
            subs['simi'] = subs.apply(lambda x: self.similarity(x['word'], x['L_QU']), axis=1)
            word_list.append(subs)

        words_df = pd.concat(word_list)
        max_similarity = words_df['simi'].argmax()
        tolerance = .85 # similarity threshold

        if max_similarity >= tolerance:
            return int(self.sub_df['OBJECTID'].loc[max_similarity])
        else:
            return None

    def process_item(self, item, spider):

        def text_cleaner(text):
            # remove trailing \n and \r
            return re.sub('\n|\r', '', ''.join(text))

        # parse price
        item['price'] = int(''.join(re.findall('\d+', item['price'])))

        # text cleaner
        item['text'] = text_cleaner(item['text'])
        item['title'] = text_cleaner(item['title'])

        # parse coord / district
        regex = r"[-+]?\d*\.\d+|\d+"
        if item['coord']:
            item['coord'] = map(float, re.findall(regex, item['coord'])[:2])

        # find sub_area from coord / text
        item['sub_area'] = self.get_sub_area(item)

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

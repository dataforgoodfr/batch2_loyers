# -*- coding: utf-8 -*-

import os, re
import pandas as pd
from difflib import SequenceMatcher

def get_sub_area(words, tolerance=.85):
    '''
    try to extract sub_area from text/adress/title
    '''

    path = os.path.realpath('.') + "\\url_scraper\\tables\\id_quartier.csv"
    sub_df = pd.read_csv(path)

    def similarity(a, b):
        '''
        get similarity ratio between 2 strings
        '''
        return SequenceMatcher(None, a, b).ratio()

    # compare the words in the adress / text to the list of areas
    max_length = max([len(i) for i in sub_df['L_QU']])
    words = [w for w in words if len(w) <= max_length]

    word_list = []
    for word in words:
        subs = sub_df[['OBJECTID', 'L_QU']].copy()
        subs['word'] = word
        subs['simi'] = subs.apply(lambda x: similarity(x['word'], x['L_QU']), axis=1)
        word_list.append(subs)

    # find word with greatest similarity
    words_df = pd.concat(word_list)
    max_similarity = words_df['simi'].argmax()

    if max_similarity >= tolerance:
        return int(sub_df['OBJECTID'].loc[max_similarity])
    else:
        return None

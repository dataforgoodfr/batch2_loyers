import pandas as pd
import matplotlib.path as mplPath
import numpy as np
import os

from geopy.distance import vincenty, great_circle
from fuzzywuzzy import fuzz, process
from operator import itemgetter

""" Python module inferring the quarter of the city from the coordinates of the flat
    get_quarter is the function of interest. It takes a tuple (latitude,longitude) as input.
    The output is a dict with 'quarter' as subarea and 'area' for the area code."""

# file path for databases and references
file_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(file_path, 'tables/quarters.csv')
refs_path = os.path.join(file_path, 'tables/refs_beta.csv')
constr_path = os.path.join(file_path, 'tables/construction_year.csv')
median_path = os.path.join(file_path, 'tables/median_an_constr.csv')

def get_polygons(coord):
    return mplPath.Path([(coord[0], coord[1]) for coord in eval(coord)])

# open data bases and references
quarter_coordinates = pd.read_csv(data_path)
quarter_coordinates["polygon"] = quarter_coordinates["coordinates"].apply(get_polygons, 0)
df_year = pd.read_csv(constr_path)
df_refs = pd.read_csv(refs_path)
df_median_year = pd.read_csv(median_path)


def get_quarter(lat_long):
    quarters = []
    for i in range(quarter_coordinates.shape[0]):
        if quarter_coordinates["polygon"][i].contains_point(lat_long):
            quarters.append(quarter_coordinates[["quarter", "area"]].ix[i])

    if len(quarters) == 1:
        return dict(quarters[0])
    else:
        return "unknown"


def get_options():
    ''' return all possible subareas as list of tuples
    '''
    subareas = quarter_coordinates['quarter'].tolist()
    subareas.append('Inconnu')
    return [(i, j) for i, j in enumerate(subareas)]

def get_choice(options, area):
    ''' return actual choice from list of possible choices
    '''
    return [i[1] for i in options].index(area)


def get_refs(item, year=2016):
    ''' return refs for given item
    '''
    refs = df_refs.ix[(df_refs['nameZone'] == item['subarea']) &
                      (df_refs['type'] == item['furnitures']) &
                      (df_refs['piece'] == item['rooms']) &
                      (df_refs['min_year'] < item['year']) &
                      (df_refs['max_year'] > item['year']) &
                      (df_refs['annee'] == year)].squeeze()

    return refs[['ref', 'refmin', 'refmaj']].to_dict()

def fuzz_quarter(desc, cutoff=85):
    ''' find the name of the sub area using 
        a fuzzy matching algorithm on the description
        data with https://github.com/seatgeek/fuzzywuzzy
        cutoff corresponds to the minimum similarity
        required to choose a given subarea. If no subarea
        is found, return None.
    '''
    try:
        names = df_refs['nameZone'].tolist()
        min_len = min([len(n) for n in names])
        words = [w for w in desc.split() if len(w) >= min_len]
        matches = [process.extractOne(w, names, score_cutoff=cutoff) 
                   for w in words]
        matches = [m for m in matches if m] # remove possible None
        return max(matches,key=itemgetter(1))[0]
    except:
        return 'Inconnu'


def fuzz_word(desc, item, cutoff=95):
    ''' find word / pair of words in the
        description of the add using fuzzy matching
        algorithm (see above). Less specific than
        quarter search. Cuttoff default set high
        because we want to be pretty conservative
        with this one.
    '''

    def find_ngrams(input_list, n):
        return zip(*[input_list[i:] for i in range(n)])

    n_words = len(item.split())
    ngrams = list(find_ngrams(desc.split(), n_words))
    match = process.extractOne(item, ngrams, score_cutoff=cutoff)
    
    if match:
        return True
    else:
        return False



def get_year(lat_long, subarea, area, method='exact'):
    ''' Get the year of construction from different methods :
    computes the shortest distance to a building with known
    construction year (1) or from the median construction
    year in the area if it fails (2). If coordinates or
    subarea are not provided, computes the area median (3).
    Return a dict with the year and the method used.
    '''
    result = {'year' : None,
              'method' : None}

    if lat_long and (subarea != 'Inconnu'):
        subcoord = df_year[df_year['subarea'] == subarea].copy()
        func = lambda x: great_circle((x['latitude'], x['longitude']), 
                                      (lat_long[0], lat_long[1])).meters
        subcoord['distance'] = subcoord.apply(func, axis=1)
        shortest_distance = subcoord.ix[subcoord['distance'].argmin()]
        year = shortest_distance['construction']
        
        if pd.isnull(year) or method == 'center':
            result['year'] = int(subcoord['construction'].median())
            result['method'] = 'sub_median'
        else:
            result['year'] = int(year)
            result['method'] = 'distance'

    else:
        year = df_median_year.ix[df_median_year['area'] == area].values
        assert len(year) == 1
        result['year'] = int(year[0][1])
        result['method'] = 'area_median'

    assert type(result) == dict
    assert type(result['year']) == int
    assert type(result['method']) == str

    return result

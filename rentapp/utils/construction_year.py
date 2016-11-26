import os, math
import pandas as pd
import numpy as np
from geopy.distance import vincenty, great_circle

file_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(file_path, 'construction_year.csv')
data = pd.read_csv(data_path)


def get_year(lat_long, subarea):
    ''' Get the year of construction from different methods :
    computes the shortest distance to a building with known
    construction year (1) or from the median construction
    year in the area if it fails (2). Return a dict with the
    year and the method used.
    '''
    result = {'year' : None,
              'method' : None}
    
    subcoord = data[data['subarea'] == subarea].copy()

    func = lambda x: great_circle((x['latitude'], x['longitude']), 
                                  (lat_long[0], lat_long[1])).meters
    
    subcoord['distance'] = subcoord.apply(func, axis=1)
    shortest_distance = subcoord.ix[subcoord['distance'].argmin()]
    year = shortest_distance['construction']
    
    if pd.isnull(year):
        result['year'] = int(subcoord['construction'].median())
        result['method'] = 'median'
    else:
        result['year'] = int(year)
        result['method'] = 'distance'

    assert type(result) == dict
    assert type(result['year']) == int
    assert type(result['method']) == str

    return result
import pandas as pd
import matplotlib.path as mplPath
import numpy as np
import os

file_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(file_path, 'quarters.csv')
refs_path = os.path.join(file_path, 'refs_beta.csv')

""" Python module inferring the quarter of the city from the coordinates of the flat
    get_quarter is the function of interest. It takes a tuple (latitude,longitude) as input.
    The output is a dict with 'quarter' as subarea and 'area' for the area code."""

def get_polygons(coord):
    return mplPath.Path([(coord[0], coord[1]) for coord in eval(coord)])


quarter_coordinates = pd.read_csv(data_path)
quarter_coordinates["polygon"] = quarter_coordinates["coordinates"].apply(get_polygons, 0)


def get_quarter(lat_long):
    quarters = []
    for i in range(quarter_coordinates.shape[0]):
        if quarter_coordinates["polygon"][i].contains_point(lat_long):
            quarters.append(quarter_coordinates[["quarter", "area"]].ix[i])

    if len(quarters) == 1:
        return dict(quarters[0])
    else:
        return "unknown"


def get_mean(quarter):
    if quarter in quarter_coordinates["quarter"].values:
        return np.round(quarter_coordinates.ix[quarter_coordinates.quarter == quarter, "mean_construction"], 0)
    else:
        return None


def get_median(quarter):
    if quarter in quarter_coordinates["quarter"].values:
        return quarter_coordinates.ix[quarter_coordinates.quarter == quarter, "median_construction"]
    else:
        return None


def get_options():
    ''' return all possible subareas as list of tuples
    '''
    subareas = quarter_coordinates['quarter'].tolist()
    return [(i, j) for i, j in enumerate(subareas)]

def get_choice(options, area):
    ''' return actual choice from list of possible choices
    '''
    return [i[1] for i in options].index(area)


def get_refs(item, year=2016):
    ''' return refs for given item
    '''
    df = pd.read_csv(refs_path)
    item['year'] = int(item['year'])
    item['rooms'] = int(item['rooms'])
    df = df[df['min_year'] < item['year']]
    df = df[df['max_year'] > item['year']]
    df = df[df['nameZone'] == item['subarea']]
    df = df[df['type'] == item['furnitures']]
    df = df[df['piece'] == item['rooms']]
    df = df[df['annee'] == year].squeeze()

    '''
    vals = df.ix[(df['nameZone'] == item['subarea']) &
                 (df['type'] == item['furnitures']) &
                 (df['piece'] == item['rooms']) &
                 (df['annee'] == year)].squeeze()
    '''
    
    return df[['ref', 'refmin', 'refmaj']].to_dict()

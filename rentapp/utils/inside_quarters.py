import pandas as pd
import matplotlib.path as mplPath
import numpy as np
import os

file_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(file_path, 'quarters.csv')

""" Python module inferrring the quarter of the city from the coordinates of the flat
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


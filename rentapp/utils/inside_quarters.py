import pandas as pd
import matplotlib.path as mplPath
import numpy as np
import os



""" Python module inferrring the quarter of the city from the coordinates of the flat
    get_quarter is the function of interest. It takes a tuple (latitude,longitude) as input.
    The output is a string."""

def get_polygons(coord):
    return mplPath.Path([(coord[0], coord[1]) for coord in eval(coord)])


quarter_coordinates = pd.read_csv(os.getcwd() + "/utils/quarters.csv")
quarter_coordinates["polygon"] = quarter_coordinates["coordinates"].apply(get_polygons, 0)


def get_quarter(lat_long):
    quarters = []
    for i in range(quarter_coordinates.shape[0]):
        if quarter_coordinates["polygon"][i].contains_point(lat_long):
            quarters.append(quarter_coordinates["quarter"][i])

    if len(quarters) == 1:
        return quarters[0]
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


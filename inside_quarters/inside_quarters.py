import pandas as pd
import matplotlib.path as mplPath



""" Python module inferrring the quarter of the city from the coordinates of the flat
    get_quarter is the function of interest. It takes a tuple (latitude,longitude) as input.
    The output is a string."""

def get_polygons(coord):
    return mplPath.Path([(coord[0], coord[1]) for coord in eval(coord)])


quarter_coordinates = pd.read_csv("quarter_shapes.csv")
quarter_coordinates["polygon"] = quarter_coordinates["coordinates"].apply(get_polygons, 0)


def get_quarter(lat_long):
    quarters = []
    for i in range(quarter_coordinates.shape[0]):
        if quarter_coordinates["polygon"][i].contains_point(lat_long):
            quarters.append(quarter_coordinates["L_QU"][i])

    if len(quarters) == 1:
        return quarters[0]
    else:
        return "unknown"




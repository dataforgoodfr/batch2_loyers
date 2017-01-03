import os
import pandas as pd
from sklearn.externals import joblib
 
def make_prediction(item):
    
    # loading features
    features = pd.Series()
    features['Price'] = item['price']
    features['Surface'] = item['surface']
    features['Furnished'] = item['furnitures']
    features['Lift'] = item['lift']
    features['Nb_rooms'] = item['rooms']
    features['Paris_2'] = 0
    features['Paris_3'] = 0
    features['Paris_4'] = 0
    features['Paris_5'] = 0
    features['Paris_6'] = 0
    features['Paris_7'] = 0
    features['Paris_8'] = 0
    features['Paris_9'] = 0
    features['Paris_10'] = 0
    features['Paris_11'] = 0
    features['Paris_12'] = 0
    features['Paris_13'] = 0
    features['Paris_14'] = 0
    features['Paris_15'] = 0
    features['Paris_16'] = 0
    features['Paris_17'] = 0
    features['Paris_18'] = 0
    features['Paris_19'] = 0
    features['Paris_20'] = 0
    features['Heating_collectif'] = 0
    features['Heating_individuel'] = 0
    features['Heating_src_electricite'] = int(item['energy']['electricite'])
    features['Heating_src_fuel'] = int(item['energy']['fuel'])
    features['Heating_src_gaz'] = int(item['energy']['gaz'])
    features['Gardien'] = item['gardien']
    features['Internet'] = item['internet']

    if item['heating'] == 'individuel':
        features['Heating_individuel'] = 1
    else:
        features['Heating_collectif'] = 1

    if item['area'] != 1:
        area_name = 'Paris_' + str(item['area'])
        features[area_name] = 1
    
    # load regressor and makes prediction
    file_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(file_path, 'models/charges_predictor.pkl')
    regressor = joblib.load(path)
    y_pred = regressor.predict(features.values.reshape(1, -1))

    print (features.values.reshape(1, -1))
    print (features)
    
    # scaling parameters
    x = 78.80818240182575
    b = 124.9107633749207
    f = 1 # to remove
    y_pred = int((x * y_pred[0] + b) / f)

    return y_pred
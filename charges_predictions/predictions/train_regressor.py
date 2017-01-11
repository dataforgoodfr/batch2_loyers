import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import sklearn
from sklearn import preprocessing, svm
from sklearn.decomposition import PCA
from sklearn.model_selection import GridSearchCV, ShuffleSplit
from sklearn.externals import joblib
import datetime

import cleaning_data_bienici
import feature_extractor_bienici
import regressor


# WE DECIDE TO WORK ON ADS FOR WHICH THE PRICE IS LESS THAN price_max €/month (in order to have a better precision)
price_max = 3000

# Get all the data
missing = ['','NaN']
bienici = pd.read_csv("../data_base_creation/results/scraping_bienici.csv", na_values = missing)

# Clean the data
cleaner = cleaning_data_bienici.DataCleaningBienici(price_max=price_max)
cleaner.fit(bienici)
bienici = cleaner.transform(bienici)
print("Data imported and cleaned")
print('Total: %s samples' %bienici.shape[0])

# Extract features
extractor = feature_extractor_bienici.FeatureExtractorBienici()
extractor.fit(bienici)
X, y = extractor.transform(bienici)
print("Features extracted")

def print_features_names(dataset, display=True):
    list_features = list(dataset.columns)
    string = "List of features (%s):" %len(list_features)
    for feature in list_features:
        string += "\n  - %s (%s)" %(feature, str(type(np.array(dataset[feature])[0])).\
                                    replace("<class 'numpy.", "").replace("'>", ""))
    if display:
        print(string)
    return string
s = print_features_names(X)

# Transform X and y to arrays
X = np.array(X)
y = np.array(y)

# Get a train and a test sets
rs = ShuffleSplit(n_splits=1, test_size=0.25)
a = rs.split(X)

for train, test in a:
    train_index = train
    test_index = test
X_test = X[test_index]
X_train = X[train_index]
y_test = y[test_index]
y_train = y[train_index]
print("Train: %s samples - Test: %s samples" %(len(y_train), len(y_test)))

# Hyperparameters tuning
tune = False
if tune:
    pass

# Train the regressor
print("Training")
reg = regressor.Regressor()
reg.fit(X_train, y_train)

# Make a test
y_hat = reg.predict(X_test)
def get_performances(y_hat, y_test):
    errors = y_test - y_hat
    error_abs = np.abs(errors)
    relative_error = error_abs / y_test * 100
    percentiles = [25, 50, 75, 90]
    print("\nAvg error: %s" %np.mean(error_abs))
    #print("Percentiles errors: %s\n" %np.percentile(error_abs, [25, 50, 75, 90]))
    print("Percentiles errors: %s (for percentiles %s)\n" %(np.percentile(error_abs, [25, 50, 75, 90]), percentiles))
    return errors, error_abs, relative_error
errors, error_abs, relative_error = get_performances(y_hat, y_test)

# Save (export) the regressor
print("Saving the regressor...")
name = 'charges_predictor.pkl'
joblib.dump(reg, name, compress=9)
print('Regressor saved as %s' %name)

# Generate the readme file
now = datetime.datetime.now()
current_date = "%s-%s-%s" %(now.year, now.month, now.day)
# Create the readme.txt file

content = """Charge prediction
-----------------

The prediction is currently based on a set of ads from bienici.com. The python code used to create this databased is in the folder ./data_base_creation

In order to train the regressor (a random forest), you need to run the script ./predictions/train_regressor.py
The regressor will be trained and saved as a pkl object in the folder ./predictions, and this readme file will be updated.

In order to import this regressor, run the 2 following lines:
>> from sklearn.externals import joblib
>> regressor = joblib.load('charges_predictor.pkl')

Note: scikit learn has to be installed.


If you want to predict the charge on a dataset X, simply run:
>> y_pred = regressor.predict(X)
where X is an array where each line is a sample (an advertisement for which the charge prediction has to be made).
The columns of X are the different features. They are (is this order):
%s

Each line of y_pred is the charge prediction for the corresonding line of X.

This regressor has been generated using a random forest, with scikit learn.
X_train: %s samples
X_test: %s samples

Here are a few metrics on the test of this regressor:
Avg error: %s
Percentiles errors: %s (for percentiles %s)

Last update: %s
""" % (s, X_train.shape[0], X_test.shape[0], np.mean(error_abs), np.percentile(error_abs, [25, 50, 75, 90]), [25, 50, 75, 90],
      current_date)
file = open('../readme.txt', 'w')
file.write(content)
file.close()
print("Readme file updated")

print("Done")
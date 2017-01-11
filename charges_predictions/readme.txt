Charge prediction
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
List of features (31):
  - price (float64)
  - surface (float64)
  - furnised (int64)
  - lift (int64)
  - nb_rooms (int64)
  - gardien (int64)
  - internet (int64)
  - paris_2 (int64)
  - paris_3 (int64)
  - paris_4 (int64)
  - paris_5 (int64)
  - paris_6 (int64)
  - paris_7 (int64)
  - paris_8 (int64)
  - paris_9 (int64)
  - paris_10 (int64)
  - paris_11 (int64)
  - paris_12 (int64)
  - paris_13 (int64)
  - paris_14 (int64)
  - paris_15 (int64)
  - paris_16 (int64)
  - paris_17 (int64)
  - paris_18 (int64)
  - paris_19 (int64)
  - paris_20 (int64)
  - heating_collective (int64)
  - heating_individual (int64)
  - heating_src_electricite (int64)
  - heating_src_fuel (int64)
  - heating_src_gaz (int64)

Each line of y_pred is the charge prediction for the corresonding line of X.

This regressor has been generated using a random forest, with scikit learn.
X_train: 4104 samples
X_test: 1369 samples

Here are a few metrics on the test of this regressor:
Avg error: 29.3253086547
Percentiles errors: [  6.592       18.723       39.51833333  67.30946667] (for percentiles [25, 50, 75, 90])

Last update: 2017-1-11

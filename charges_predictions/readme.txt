Charge prediction
-----------------

The predictor is saved as a pkl object in the folder ./predictions

In order to import this regressor, run the 2 following lines:
>> from sklearn.externals import joblib
>> regressor = joblib.load('charges_predictor.pkl')

Note: scikit learn has to be installed.

This object (regressor) is a scikit-learn random forest.

If you want to predict the charge on a dataset X, run:
>> y_pred = regressor.predict(X)

X has to be an array where each line is a sample (an advertisement for which the charge prediction has to be made).
The columns of X are the different features. They are (is this order):
 - Price
 - Surface
 - Furnished
 - Lift
 - Nb_rooms
 - Paris_2
 - Paris_3
 - Paris_4
 - Paris_5
 - Paris_6
 - Paris_7
 - Paris_8
 - Paris_9
 - Paris_10
 - Paris_11
 - Paris_12
 - Paris_13
 - Paris_14
 - Paris_15
 - Paris_16
 - Paris_17
 - Paris_18
 - Paris_19
 - Paris_20
 - Heating_collectif
 - Heating_individuel
 - Heating_src_electricite
 - Heating_src_fuel
 - Heating_src_gaz
 - Gardien
 - Internet

All these features are generated on the test set in the notebook ./predictions/charge_prediction.ipynb

Each line of y_pred is the charge prediction for the corresonding line of X.

This regressor has been generated using a random forest, with scikit learn.
X_train: 3546 samples
X_test: 1183 samples

Here are a few metrics on the test of this regressor:
Avg error: 29.6115296495
Percentiles errors: [  7.853   19.157   42.0885  70.578 ] (for percentiles [25, 50, 75, 90])

Last update: 2016-12-12

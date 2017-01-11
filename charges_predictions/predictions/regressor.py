from sklearn.pipeline import Pipeline                                            
from sklearn.base import BaseEstimator                                           
import numpy as np
from sklearn import preprocessing 
from sklearn.ensemble import RandomForestRegressor
                                                                                 
class Regressor(BaseEstimator):                                                  
    def __init__(self, n_estimators=1000):
        
        # Models by default:
        
        self.reg = Pipeline([
            ('forest', RandomForestRegressor(n_estimators=n_estimators, n_jobs=-1)) 
        ])
                                                                                 
    def fit(self, X, y):
        # Normalize the data
        self.scaler = preprocessing.StandardScaler(with_mean=True, with_std=True).fit(X)
        X = self.scaler.transform(X)
        
        self.mean_y, self.std_y = np.mean(y), np.std(y)
        y = (y - self.mean_y) / self.std_y
        
        self.reg.fit(X, y)
            
    def predict(self, X): 
        # Normalize the data
        X = self.scaler.transform(X)
        
        # Make the regression
        y_pred = self.reg.predict(X)
        
        # Rescale
        y_pred = y_pred * self.std_y + self.mean_y
        
        return y_pred
    
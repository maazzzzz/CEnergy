from sklearn.externals import joblib
import numpy as np
import os
import random
import sklearn
import pandas as pd
from sklearn.model_selection import train_test_split


loaded_rf = joblib.load('random_forest_best.sav')
loaded_et = joblib.load('extra_trees_best.sav')
loaded_gb = joblib.load('gradient_boosting_best.sav')

# Normalization Values
mean_size=1404594.7477361772
std_size=2777144.033689179    
energy_max=99.29
energy_min=0.01



def predict(arr,num=1):
    if(num==1):
        arr=np.array(arr)
        arr=arr.reshape(1, -1)
    
    rf=loaded_rf.predict(arr)
    gb=loaded_gb.predict(arr)
    et=loaded_et.predict(arr)

    return rf,et,gb,(rf+et+gb)/3.0


def print_prediction(pred):
    diff=energy_max-energy_min

    print "Random Forest: ",(pred[0]*diff)+energy_min
    print "Extra Trees: ",(pred[1]*diff)+energy_min
    print "Gradient Boosting: ",(pred[2]*diff)+energy_min
    print "Ensemble: ",(pred[3]*diff)+energy_min
    

def main():
    
    # Test Record
    arr=[15,8,11,3,2,3,3,28]
    arr[7]=(arr[7]-mean_size)/std_size

    pred=predict(arr,1)
    print_prediction(pred)


main()





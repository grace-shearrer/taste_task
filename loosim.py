"""

simulate leave-one-out crossvalidation

"""

import numpy as N
from sklearn import cross_validation
from sklearn import datasets

data=sklearn.datasets.make_regression(n_samples=100,n_features=2,
    n_informative=2,n_targets=1,noise=1.0)
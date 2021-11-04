import numpy as np
import time


class Regressor:

    @staticmethod
    def xtoX(x, degree=1):
        X = np.empty((len(x), degree + 1))
        for i in range(degree + 1):
            X[:,i] = x**i
        return X

    def fit(self, x, y):
        X, Y = self.xtoX(x, self.d), y
        time.sleep(np.random.randint(10, 30)) # simulate slow computation
        self.B = np.linalg.pinv((X.T).dot(X)).dot((X.T).dot(Y))

    def predict(self, x):
        return self.xtoX(x, self.d).dot(self.B)


class MultivariateRegressor(Regressor):

    def __init__(self):
        self.d = 1


class PolynomialRegressor(Regressor):

    def __init__(self, degree):
        self.d = degree

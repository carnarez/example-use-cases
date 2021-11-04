import numpy as np

np.random.seed(8)


class InputData:
    
    def __init__(self, b=-1.0, e=1.0):
        self.x = np.linspace(b, e)
        self.y = self.f(self.x)

    @staticmethod
    def f(x):
        return 3 + 0.4*x - 3.0*x**2 + 2.0*x**3

    @staticmethod
    def g(x):
        pass

    @staticmethod
    def noise(arr, fuzz):
        return arr + arr*np.random.uniform(-fuzz, fuzz, len(arr))

import numpy as np


class Evaluate:

    def __init__(self, y):
        self.y = y

    def _sse(self, y):
        return ((y - self.y)**2).sum()

    def _mse(self, y):
        return self._sse(y)/len(self.y)

    def _r2(self, y):
        return 1 - self._sse(y)/((self.y - self.y.mean())**2).sum()

    def score(self, y, algo='mse'):
        if algo == 'sse':
            return self._sse(y)
        elif algo == 'mse':
            return self._mse(y)
        elif algo == 'r2':
            return self._r2(y)
        else:
            raise ValueError('Evaluation algorithm not implemented')

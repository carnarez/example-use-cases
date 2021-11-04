import falcon
import io
import json
import logging
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import os
import time


logging.basicConfig(datefmt='%Y/%m/%d %X', format='%(asctime)s - %(message)s', level='INFO')
logger = logging.getLogger(__name__)


def timeit(func):
    def wrapper(*args, **kwargs):
        t0 = time.time()
        output = func(*args, **kwargs)
        logger.info(f"{os.environ['HOSTNAME']} finished request in {time.time() - t0:.2f} seconds")
        return output
    return wrapper


class Plot:

    def __init__(self):
        self.nints = 50_000_000
        self.niter = 200
        self.scale = 200
        self.zreal = -0.1
        self.zimag = 0.65

    def compute(self):
        raise NotImplementedError

    def render(self, array):
        out = io.BytesIO()

        fig, ax = plt.subplots(figsize=(10, 10))
        fig = ax.imshow(array, interpolation='nearest', cmap='Blues')
        plt.axis('off')
        plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off', labelleft='off', labeltop='off', labelright='off', labelbottom='off')
        plt.savefig(out, format='png', bbox_inches='tight', pad_inches=0.0)

        return out.getvalue()

    def on_get(self, req, resp):
        resp.text = json.dumps({
            'julia': {
                'niter': self.niter,
                'scale': self.scale,
                'zreal': self.zreal,
                'zimag': self.zimag
            },
            'mandelbroot': {
                'niter': self.niter,
                'scale': self.scale
            },
            'sqrt': {
                'nints': self.nints
            }
        })


class Julia(Plot):

    @timeit
    def compute(self):
        array = np.zeros((self.scale, self.scale))
 
        c = complex(self.zreal, self.zimag)
        for ix in range(self.scale):
            for iy in range(self.scale):
                z = complex(ix/self.scale*3 - 1.5, iy/self.scale*3 - 1.5)
                for i in range(self.niter):
                    z = z**2 + c
                    if abs(z) > 10:
                        break
                array[ix, iy] = float(i + 1)/self.niter
 
        return array

    def on_get(self, req, resp):
        self.niter = int(req.params.get('niter', 200))
        self.scale = int(req.params.get('scale', 200))
        self.zreal = float(req.params.get('zreal', -0.1))
        self.zimag = float(req.params.get('zimag', 0.65))

        resp.text = self.render(self.compute())
        resp.content_type = 'image/png'


class Mandelbrot(Plot):

    @timeit
    def compute(self):
        array = np.zeros((self.scale, self.scale))
 
        for ix in range(self.scale):
            for iy in range(self.scale):
                c = complex(ix/self.scale*3 - 2.0, iy/self.scale*3 - 1.5)
                z = 0
                for i in range(self.niter):
                    z = z**2 + c
                    if abs(z) > 2:
                        break
                array[iy, ix] = float(i + 1)/self.niter
 
        return array

    def on_get(self, req, resp):
        self.niter = int(req.params.get('niter', 200))
        self.scale = int(req.params.get('scale', 200))

        resp.text = self.render(self.compute())
        resp.content_type = 'image/png'


class SquareRoot(Plot):

    @timeit
    def compute(self):
        return np.sqrt(np.random.randint(time.time(), size=self.nints))

    def on_get(self, req, resp):
        self.nints = int(req.params.get('nints', 50_000_000))

        self.compute()
        resp.text = json.dumps(f'{self.nints} square roots calculated')


api = falcon.App()
api.add_route('/', Plot())
api.add_route('/julia', Julia())
api.add_route('/mandelbrot', Mandelbrot())
api.add_route('/sqrt', SquareRoot())

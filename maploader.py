import random
import numpy as np

class MapLoader:
    def perlin(self, x, y, seed=0):
        def lerp(a, b, x):
            "linear interpolation"
            return a + x * (b - a)

        def fade(t):
            "6t^5 - 15t^4 + 10t^3"
            return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3

        def gradient(h, x, y):
            "grad converts h to the right gradient vector and return the dot product with (x,y)"
            vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
            g = vectors[h % 4]
            return g[:, :, 0] * x + g[:, :, 1] * y

        # permutation table
        np.random.seed(seed)
        p = np.arange(256, dtype=int)
        np.random.shuffle(p)
        p = np.stack([p, p]).flatten()
        # coordinates of the top-left
        xi = x.astype(int)
        yi = y.astype(int)
        # internal coordinates
        xf = x - xi
        yf = y - yi
        # fade factors
        u = fade(xf)
        v = fade(yf)
        # noise components
        n00 = gradient(p[p[xi] + yi], xf, yf)
        n01 = gradient(p[p[xi] + yi + 1], xf, yf - 1)
        n11 = gradient(p[p[xi + 1] + yi + 1], xf - 1, yf - 1)
        n10 = gradient(p[p[xi + 1] + yi], xf - 1, yf)
        # combine noises
        x1 = lerp(n00, n10, u)
        x2 = lerp(n01, n11, u)
        return lerp(x1, x2, v)

    def get_map(self, h, w, max_tile, seed=0):
        liny = np.linspace(0, 5, h, endpoint=False)
        linx = np.linspace(0, 5, w, endpoint=False)
        x, y = np.meshgrid(linx, liny)
        m=self.perlin(x, y, seed=seed)
        m=((m-m.min())*max_tile/(m.max()-m.min())).astype(int)
        return m.tolist()

    def get_chance_map(self, h, w, min_tile=0, max_tile=1):
        return [[random.uniform(min_tile,max_tile) for j in range(w)] for i in range(h)]

    def get_inits(self, h, w, difficulty, seed=int(random.random()*1000), min_chance_stoc=1,
                  foodAddScore=9, foodScoreMulti=1, turningCost=5,
                  consume_tile=False, winScore=38):
        difficulty=max(winScore/foodScoreMulti//difficulty,1)

        return {'foodGrid': self.get_map(h,w, difficulty, seed=seed),
                'chance_map': self.get_chance_map(h,w,min_chance_stoc),
                "consume_tile": consume_tile, "turningCost": turningCost,
                "foodAddScore": foodAddScore,
                "foodScoreMulti": foodScoreMulti, "winScore": winScore}
import random

from component.base import BaseComponent
from shapely.geometry.multipoint import MultiPoint


class Island(BaseComponent):
    seed = None

    persists = ['seed']

    def initialize(self):
        if self.seed is None:
            self.generate()

    def generate(self):
        # much random
        self.seed = 1  # random.getrandbits(64)
        points = [(random.uniform(-2048.0, 2048.0), random.uniform(-2048.0, 2048.0)) for _ in range(1000)]

        # extract convex hull
        hull = MultiPoint(points).convex_hull
        points = list(hull.boundary.coords)

        tpoly = self.entity.add_component(
            'TerrainPolygon',
            points=points
        )
        self.entity.set_dirty()


class TerrainPolygon(BaseComponent):
    points = None
    persists = ['points']

    def initialize(self):
        print(self.points)

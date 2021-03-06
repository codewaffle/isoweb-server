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

        random.seed(self.seed)

        points = [(random.uniform(-15.0, 15.0), random.uniform(-15.0, 15.0)) for _ in range(15)]

        # extract convex hull
        hull = MultiPoint(points).convex_hull
        points = list(hull.boundary.coords)

        self.entity.Position.x = (hull.bounds[0] + hull.bounds[2]) / 2
        self.entity.Position.y = (hull.bounds[1] + hull.bounds[3]) / 2

        self.entity.Position.w = hull.bounds[2] - hull.bounds[0]
        self.entity.Position.h = hull.bounds[3] - hull.bounds[1]

        self.entity.Position._update()

        tpoly = self.entity.add_component(
            'StaticPolygon',
            points=points
        )
        self.entity.set_dirty()


class StaticPolygon(BaseComponent):
    points = None
    texture = 'tiles/tile_grass.png'

    exports = ['points', 'texture']
    persists = ['points']

    def initialize(self):
        pass

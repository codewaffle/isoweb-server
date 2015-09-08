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

        self.entity.Position.x = (hull.bounds[0] + hull.bounds[2]) / 2
        self.entity.Position.y = (hull.bounds[1] + hull.bounds[3]) / 2

        self.entity.Position.w = hull.bounds[2] - hull.bounds[0]
        self.entity.Position.h = hull.bounds[3] - hull.bounds[1]

        self.entity.Position._update()

        tpoly = self.entity.add_component(
            'TerrainPolygon',
            points=points
        )
        self.entity.set_dirty()


class TerrainPolygon(BaseComponent):
    points = None
    texture = 'tiles/tile_grass.png'

    exports = ['points', 'texture']
    persists = ['points']

    def initialize(self):
        pass

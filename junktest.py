from random import uniform
from phys import Space, CircleBody
from shapely.geometry import MultiPoint

space = Space()

body = CircleBody(mass=1.0, radius=1.0)
space.add(body)

for x in range(100):
    space.step(0.1)
    print('woo!', body.position)


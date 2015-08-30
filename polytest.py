from timeit import timeit
import math
import shapely.speedups
shapely.speedups.enable()
from isoweb_time import clock


from random import uniform
from mathx.shapely_affine import translate, rotate
from shapely.geometry import MultiPoint
from shapely.geometry.polygon import Polygon

points = [(uniform(-2048.0, 2048.0), uniform(-2048.0, 2048.0)) for _ in range(100000)]

island = MultiPoint(points).convex_hull

boat = Polygon([(-1,-2), (-1, 2), (1, 2), (1, -2)])
print(boat)

print('timin')


intersects = None


def move_and_check():
    global boat, intersects
    boat = translate(boat, 1.0)
    val = boat.intersects(island)

    if val != intersects:
        print('Changed from {} to {}'.format(intersects, val))
        intersects = val


# print(timeit("move_and_check()", number=10000, setup="from __main__ import move_and_check")/10)
n = 0
i = 0
start = clock()
while True:
    if clock() > n:
        print('i: {}    i/s: {}'.format(i, i/(clock()-start)))
        n = clock() + 1.0

    boat = translate(boat, 1.0)
    boat = rotate(boat, math.pi/10.0)
    test = boat.intersects(island)
    i += 1

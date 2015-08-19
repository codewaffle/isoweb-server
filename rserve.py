import random
import math
from config import DB_DIR
import logbook
from logbook.handlers import StderrHandler
from mathx.vector2 import Vector2
from twisted.internet.defer import inlineCallbacks
from util import sleep

StderrHandler(level=logbook.DEBUG).push_application()
import logging
logging.basicConfig(level=logging.DEBUG)


from island import Island
from network.player import PlayerWebsocket
from twisted.internet import reactor, defer, task


from autobahn.twisted.websocket import WebSocketServerFactory

from entitydef import load_defs

import os
spawn = False


try:
    os.stat(DB_DIR)
except OSError:
    os.makedirs(DB_DIR)
    spawn = True

load_defs()

factory = WebSocketServerFactory()
factory.protocol = PlayerWebsocket

reactor.listenTCP(10000, factory)

factory.island = island = Island(0)
island.start()

def spawn_crap(name, num, scalebase=1.0, modscale=0.0, rot=False):
    for x in range(num):
        ent = island.spawn(name, pos=Vector2.random_inside(5))

        if modscale:
            ent.Sprite.data.scale = scalebase + random.random() * modscale
            ent.Position.data.z = ent.Sprite.data.scale / 2.

        if rot:
            ent.Position.data.r = 2.*math.pi * random.random()

#@inlineCallbacks
def spawn_all():
    spawn_crap('crate', 1, rot=True)
    spawn_crap('backpack', 1, rot=True)

    for x in range(5000):
        island.spawn('tree', pos=Vector2(random.uniform(-128, 128), random.uniform(-128, 128))).Position.data.r = 2.*math.pi * random.random()

    for x in range(5000):
        island.spawn('chicken', pos=Vector2(random.uniform(-256, 256), random.uniform(-256, 256))).Position.data.r = 2.*math.pi * random.random()

    island.spawn('testhouse', pos=Vector2(0,0))

    """
    seq = ghalton.Halton(2)
    seq.get(2048)

    for x in range(100):
        for t in range(1, 50):
            island.spawn('tree', pos=(Vector2(*seq.get(1)[0])-Vector2(0.5, 0.5))*t*100).Position.data.r = 2.*math.pi * random.random()
        yield sleep(0.1)
    """


if spawn:
    spawn_all()

reactor.run()


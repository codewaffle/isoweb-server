import random
import math
import logbook
from logbook.handlers import StderrHandler
from mathx import Vector2

StderrHandler(level=logbook.DEBUG).push_application()
import logging
logging.basicConfig(level=logging.DEBUG)


from island import Island
from network.player import PlayerWebsocket
from twisted.internet import reactor, defer, task


from autobahn.twisted.websocket import WebSocketServerFactory

from entitydef import load_defs
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

def spawn_all():
    spawn_crap('crate', 1, rot=True)
    spawn_crap('backpack', 1, rot=True)
spawn_all()

reactor.run()

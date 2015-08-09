import bootstrap

import websockets
import asyncio


from config import DB_DIR


from math import pi, cos, sin, exp
import random
from mathx import Vector2

import socket
import logbook
from network.player import PlayerWebsocket


def reset_db():
    logbook.warn("Resetting Database")
    import shutil, os

    try:
        shutil.rmtree(DB_DIR)
    except:
        pass

    os.mkdir(DB_DIR)
    return True

respawn = False
respawn = reset_db()


from entitydef import load_defs
load_defs()

from component import c
from island import Island


import logging
logging.basicConfig(level=logging.DEBUG)

island = Island(0)
island.start()


def spawn_crap(name, num, scalebase=1.0, modscale=0.0, rot=False):
    for x in range(num):
        ent = island.spawn(name, pos=Vector2.random_inside(5))

        if modscale:
            ent.Sprite.data.scale = scalebase + random.random() * modscale
            ent.Position.data.z = ent.Sprite.data.scale / 2.

        if rot:
            ent.Position.data.r = 2.*pi * random.random()

def spawn_all():

    #gevent.sleep(5)
    #for x in range(-50, 50):
        #for y in range(-50, 50):
        #    t = island.spawn('tree', pos=Vector2(x, y)*8)
        #gevent.sleep(0.05)

    # spawn_crap('tree', 3, scalebase=1.5, modscale=1.0)
    # spawn_crap('tree', 20, scalebase=1.5, modscale=1.0)
    # spawn_crap('rock', 3, scalebase=1.0, modscale=4.0)

    spawn_crap('crate', 1, rot=True)
    spawn_crap('backpack', 1, rot=True)

    # spawn_crap('log', 15)
    # spawn_crap('stone_axe', 1, rot=True)

    # return

    #seq = ghalton.Halton(2)
    #seq.get(2048)

    #for x in range(100):
    #    for t in range(100):
    #        island.spawn('tree', pos=(Vector2(*seq.get(1)[0])-Vector2(0.5, 0.5))*2048).Position.data.r = 2.*pi * random.random()

if respawn:
    spawn_all()

@asyncio.coroutine
def ws_test(ws, path):
    print(path)
    ps = PlayerWebsocket(ws)
    return ps.on_connect(island)



#ws_server = websockets.serve(ws_test, port=10000)

#logbook.info('starting websocket')
#ws_server.start()
# disable nagle's
#ws_server.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

logbook.info('waiting')

def spawn_things():
    pass

print('reached end')

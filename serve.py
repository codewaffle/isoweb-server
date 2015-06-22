import random
import gevent

from gevent.monkey import patch_all
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.server import WebSocketServer
from entity.player.player import Player
from entity.player.socket import PlayerSocket

from world.island import Island

patch_all(ssl=False)

import logging
logging.basicConfig(level=logging.DEBUG)

from gevent import pywsgi
from web_app import create_flask_app

island = Island(42)

def ws_app(env, start):
    if env['PATH_INFO'] == '/player':
        ps = PlayerSocket(env['wsgi.websocket'])
        # attach to player
        ps.player = Player()
        ps.player.position.x = random.random() * 50
        ps.player.position.y = random.random() * 50
        ps.player.bearing = random.random() * 360 - 180
        ps.player.socket = ps

        island.players.append(ps.player)
        island.entities.append(ps.player)

        return ps.on_connect()

ws_server = WebSocketServer(
    ('', 10000),
    ws_app,
    handler_class=WebSocketHandler
)

web_server = pywsgi.WSGIServer(
    ("", 9000),
    create_flask_app()
)


print 'starting webserver'
web_server.start()

print 'starting websocket'
ws_server.start()

print 'starting island'
island.start()

print 'waiting'
gevent.wait()

from gevent.monkey import patch_all
from logbook.queues import ZeroMQHandler

from world.region import Region

patch_all(ssl=False)

import gevent
import socket
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.server import WebSocketServer
import logbook
logbook.default_handler.level = logbook.DEBUG
from network.player import PlayerWebsocket

from world.island import Island


import logging
logging.basicConfig(level=logging.DEBUG)

from gevent import pywsgi
from web.app import create_app

ws_zmq_handler = ZeroMQHandler('tcp://127.0.0.1:9009', bubble=True)

region = Region()
island = Island(42)
island.log_handler = ws_zmq_handler
region.add_island(island)

def ws_app(env, start):
    if env['PATH_INFO'] == '/player':
        ws = env['wsgi.websocket']
        ws.stream.handler.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        with ws_zmq_handler:
            ps = PlayerWebsocket(ws)

            return ps.on_connect(island)

ws_server = WebSocketServer(
    ('', 10000),
    ws_app,
    handler_class=WebSocketHandler
)

web_server = pywsgi.WSGIServer(
    ("", 9000),
    create_app()
)

logbook.info('starting webserver on :{0}', web_server.server_port)
web_server.start()

logbook.info('starting websocket on :{0}', ws_server.server_port)
ws_server.start()
# disable nagle's
ws_server.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

logbook.info('waiting')
gevent.wait()

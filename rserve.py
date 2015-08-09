import logbook
from logbook.handlers import StderrHandler
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

reactor.run()

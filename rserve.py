from time import clock
from network.player import PlayerWebsocket
from twisted.internet import reactor, defer, task
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import deferLater

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from util import sleep

factory = WebSocketServerFactory()
factory.protocol = PlayerWebsocket

reactor.listenTCP(10000, factory)

reactor.run()

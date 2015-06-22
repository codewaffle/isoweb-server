import random
import ujson as json
from geventwebsocket import WebSocketError


class PlayerSocket(object):
    def __init__(self, ws):
        self.ws = ws
        self.player = None

    def on_connect(self):
        self.handle_login()

        while self.handle(self.recv()):
            pass

        self.handle_logout()

    def recv(self):
        data = self.ws.receive()
        if data is None:
            return None

        # TODO : this is no longer json..
        return ujson.loads(data)

    def send(self, data):
        try:
            self.ws.send(data, binary=True)
        except WebSocketError:
            return self.on_disconnect()

    def handle_login(self):
        # assign player to island, send initial bla bla bla
        self.player.id = random.randint(1, 1234)

    def handle_logout(self):
        pass

    def handle(self, data):
        if data is None:
            return False

        # players can set their own bearing

        if 'bear' in data:
            self.player.bearing = data['bear']
        if 'move' in data:
            self.player.move_target = data['move']

        return True

    def on_disconnect(self):
        # TODO : ugh, we need to pop the player out of here.. but they belong to island atm and it's dumb.
        print 'bang'
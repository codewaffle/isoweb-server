from gevent import sleep
import json
import random

class WebSocketApp(object):
    def __call__(self, environ, start_response):
        ws = environ['wsgi.websocket']
        x = 0
        while True:
            data = json.dumps({'x': x, 'y': random.randint(1, 5)})
            ws.send(data)
            x += 1
            sleep(0.25)

def create_ws_app():
    return WebSocketApp()
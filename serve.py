from gevent.monkey import patch_all

patch_all(ssl=False)

import logging
logging.basicConfig(level=logging.DEBUG)

from gevent import pywsgi, sleep
from geventwebsocket.handler import WebSocketHandler
from web_app import create_flask_app
from websocket_app import create_ws_app


ws_server = pywsgi.WSGIServer(
    ("", 10000), create_ws_app(),
    handler_class=WebSocketHandler
)

web_server = pywsgi.WSGIServer(
    ("", 9000),
    create_flask_app()
)

ws_server.start()
web_server.serve_forever()

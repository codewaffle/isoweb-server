from flask import Flask
from proto import blueprint as proto_bp


class ISOWebApp(Flask):
    pass

def create_flask_app():
    app = ISOWebApp(__name__, static_folder='../client/dist', static_path='/dist')
    app.register_blueprint(proto_bp)

    return app

from flask import Flask
from web import views


class ISOWebApp(Flask):
    pass


def create_app():
    app = ISOWebApp(__name__, static_folder='../../client/dist', static_path='/dist')
    app.secret_key = 'D8EV7BxytBnUDgwDEabNHMKGXWoWoABDfbVqJpRDki29rkEprlTvh1pu88N804upa9oRpQTNvkY59GL'
    app.register_blueprint(views.blueprint)

    return app

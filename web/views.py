from flask import render_template, session, redirect
from flask.blueprints import Blueprint
from flask.helpers import url_for, send_from_directory
from config import ASSET_DIR

blueprint = Blueprint(__name__, __name__)
route = blueprint.route

@route('/login')
def login():
    pass

@route('/logout')
def logout():
    pass

@route('/')
def play():
    #if not session.get('player_id'):
    #    return redirect(url_for('.login'))

    return render_template('index.html')

@route('/assets/<path:fn>')
def assets_static(fn):
    return send_from_directory(ASSET_DIR, fn)

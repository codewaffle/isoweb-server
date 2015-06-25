from flask import render_template, session, redirect
from flask.blueprints import Blueprint
from flask.helpers import url_for

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
    if not session.get('player_id'):
        return redirect(url_for('.login'))

    return render_template('index.html')


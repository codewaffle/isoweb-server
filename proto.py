from flask import render_template
from flask.blueprints import Blueprint

blueprint = Blueprint('proto', __name__)

@blueprint.route('/')
def go():
    return render_template('index.html')


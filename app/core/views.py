from flask import (
    Blueprint,
    redirect,
    url_for,
)

bp_core = Blueprint('core', __name__)

@bp_core.route('/', endpoint='index', methods=['GET'])
def index():
    return redirect(url_for('core.teams_list'))
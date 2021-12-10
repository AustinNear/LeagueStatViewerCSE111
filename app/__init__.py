import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # app.debug = True
    # app.config['DEBUG'] = True

    app.url_map.strict_slashes = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

    app.config['SECRET_KEY'] = 'Q0+o,X?I)j@W-K<M.u&fP:s6!?R3(HOPD<),=5M8&hzIMi&iZvZzQ|BVLIg4i/@u'

    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, '..', 'webapp-database.sqlite')

    db.init_app(app)
    csrf.init_app(app)

    # register blueprints
    from app.core import bp_core
    app.register_blueprint(bp_core, url_prefix='/')

    return app
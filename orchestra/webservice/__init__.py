import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# administration
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from flask_celeryext import FlaskCeleryExt
from .celery_utils import make_celery
ext_celery = FlaskCeleryExt(create_celery_app=make_celery)

from . import tasks

def create_app(test_config=None):
    app = Flask(__name__)
    # application configuration
    #app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.instance_path}/{__name__}.sqlite3"
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://orchestra:orchestra@orchestra_db/orchestra/"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
    app.config["SECRET_KEY"]="dev"

    # celery
    app.config["CELERY_BROKER_URL"] = "redis://127.0.0.1:6379/0"
    app.config["CELERY_RESULT_BACKEND"] = "redis://127.0.0.1:6379/0"

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
        os.makedirs(os.path.join(app.instance_path, "archive"))
    except OSError:
        pass
    
    # initialize database
    from .db import init_app, db
    init_app(app)

    # login
    from .auth import init_login
    init_login(app)

    # administration
    from .admin import init_admin
    init_admin(app)

    # REST API
    from .rest import init_app
    init_app(app)

    # celery
    ext_celery.init_app(app)

    # add some functions for jinja2 templates
    import time
    app.jinja_env.globals.update(running_time=lambda t: time.time() - t)


    @app.shell_context_processor
    def ctx():
        return {"app":app, "db": db}
    
    return app


import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# administration
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

def create_app(test_config=None):
    app = Flask(__name__)
    # application configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{__name__}.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
    app.config["SECRET_KEY"]="dev"

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
    
    return app


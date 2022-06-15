import flask_login as login

from ..db import get_db
from .models import User

def init_login(app):
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return get_db().session.query(User).get(user_id)

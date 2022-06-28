from flask import redirect, url_for
from flask_admin import Admin
from flask_admin.menu import MenuLink

# redis console
#from redis import Redis
#from flask_admin.contrib import rediscli

from .views import OrchestraAdminIndexView

from ..models import Module, Task
from ..views import ModuleView, TaskView
from ..auth.models import User
from ..auth.views import UserView

from .menu import LogoutMenuLink, FlowerMenuLink
 
def init_admin(app):
    from ..db import init_app, db
    admin = Admin(name="orchestra", template_mode="bootstrap3", index_view=OrchestraAdminIndexView())
    admin.init_app(app)
    admin.add_view(UserView(User, db.session))
    admin.add_view(ModuleView(Module, db.session))
    admin.add_view(TaskView(Task, db.session))

    # redis
    #admin.add_view(rediscli.RedisCli(Redis()))

    admin.add_link(FlowerMenuLink(name="Monitor", category="", url="http://dashboard:5555"))
    admin.add_link(LogoutMenuLink(name="Logout", category="", url="/admin/logout"))


    # route root URL to admin
    @app.route("/")
    def index():
        return redirect(url_for("admin.index"))



from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request
import flask_login as login


class UserView(ModelView):
    column_display_pk = True
    #column_searchable_list = ("name",)
    def is_accessible(self):
        return login.current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login", next=request.url))
 

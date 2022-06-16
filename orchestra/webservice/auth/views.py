from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request
import flask_login as login

from wtforms import fields
from werkzeug.security import generate_password_hash


class PasswordField(fields.StringField):
    def process_data(self, value):
        self.data = ""
        self.orig_hash = value
    def process_formdata(self, valuelist):
        value = ""
        if valuelist:
            value = valuelist[0]
        if value:
            self.data = generate_password_hash(value)
        else:
            self.data = self.orig_hash


class UserView(ModelView):
    column_display_pk = True
    column_searchable_list = ("username",)
    form_overrides = dict(password=PasswordField)
    form_widget_args = dict(placeholder="Enter new password")
    def is_accessible(self):
        return login.current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login", next=request.url))
    def is_action_allowed(self, name):
        r = super().is_action_allowed(name)
        print(f"\n\tis_action_allowed({name}) -> {r}\n")
        return r
 

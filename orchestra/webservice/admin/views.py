from flask import url_for, redirect, render_template, request, flash
import flask_admin as admin
import flask_login as login
from flask_admin import helpers, expose

from ..db import get_db

from ..auth.forms import *
from ..auth.models import User

class OrchestraAdminIndexView(admin.AdminIndexView):
    @expose("/")
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        return super().index()

    @expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            try:
                login.login_user(user)
            except Exception:
                flash("Unknown username or password")
                return redirect(url_for(".index"))
        if login.current_user.is_authenticated:
            return redirect(url_for(".index"))
        link = "<p>Don\'t have an account? <a href='" + url_for(".register_view") + "'>Click here to register.</a></p>"
        self._template_args["form"] = form
        self._template_args["link"] = link
        return super().index()
    @expose("/register/", methods=("GET", "POST"))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()
            form.populate_obj(user)
            user.password = generate_password_hash(form.password.data)
            db = get_db()
            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for(".index"))
        link = "<p>Already have an account? <a href='" + url_for(".login_view") + "'>Click here to log in.</a></p>"
        self._template_args["form"] = form
        self._template_args["link"] = link
        return super().index()

    @expose("/logout/")
    def logout_view(self):
        login.logout_user()
        return redirect(url_for(".index"))



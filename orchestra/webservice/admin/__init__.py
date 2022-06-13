from werkzeug.exceptions import HTTPException
from flask import Flask, request, send_from_directory, redirect, Response
from flask_admin import Admin, AdminIndexView

from orchestra.module.info import ModuleInfo
from orchestra.module.manager import ModuleManager

class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(message, Response(
            "You could not be authenticated. Please refresh the page.", 401,
            {"WWW-Authenticate": "Basic realm='Login Required'"}
            ))

class OrchestraAdminIndexView(AdminIndexView):
    def __init__(self, basic_auth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.basic_auth = basic_auth
    def is_accessible(self):
        if not self.basic_auth.authenticate():
            raise AuthException("You are not authenticated")
        else:
            return True
    def inaccessible_callback(self, name, **kwargs):
        return redirect(self.basic_auth.challenge())
    def render(self, template, **kwargs):
        # get the list of modules installed
        modules = list(ModuleManager().iter_modules())
        return super().render(template, modules=modules)



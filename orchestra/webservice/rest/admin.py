from flask_admin import AdminIndexView

class OrchestraAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if not basic_auth.authenticated():
            raise AuthException("You are not authenticated")
        else:
            return True
    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())

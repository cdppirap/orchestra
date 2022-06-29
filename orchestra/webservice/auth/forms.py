from wtforms import form, fields, validators
from werkzeug.security import generate_password_hash, check_password_hash

from ..db import get_db
from .models import User

#db = get_db()

class LoginForm(form.Form):
    username = fields.StringField(validators=[validators.DataRequired()])
    password = fields.StringField(validators=[validators.DataRequired()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError("Invalid user")

        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError("Invalid password")

    def get_user(self):
        return get_db().session.query(User).filter_by(username=self.username.data).first()

class RegistrationForm(form.Form):
    username = fields.StringField(validators=[validators.DataRequired()])
    email = fields.StringField()
    password = fields.StringField(validators=[validators.DataRequired()])

    def validate_login(self, field):
        if get_db().session.query(User).filter_by(username=self.username.data).count() > 0:
            raise validators.ValidationError("Duplicate username")
       

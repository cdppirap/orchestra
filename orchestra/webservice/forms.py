import os
import tempfile
import zipfile
import json
import uuid

import werkzeug.datastructures
from werkzeug.utils import secure_filename

from flask import current_app, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms import validators

from .models import Module

from .validators import OneOrTheOther, ModuleUniqueNameValidator 

class ModuleCreateForm(FlaskForm):
    repository = StringField("Module Github repository", validators=[validators.Optional(),
        OneOrTheOther(["repository", "archive"]),
        validators.URL()])
    archive = FileField("Module archive", validators=[validators.Optional(),
        OneOrTheOther(["repository", "archive"]),
        ModuleUniqueNameValidator()]
        )


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField

from .models import Module

class ModuleCreateForm(FlaskForm):
    name = StringField("Module name")
    repository = StringField("Module repository")
    archive = FileField("Module archive")
    json = StringField("JSON")
    context_id = StringField("Context id")
    def validate_repository(self, field):
        if len(field.data)==0:
            return True
        return field.data.startswith("https://") and field.data.endswith(".git")
    def validate_archive(self, field):
        return field.data.filename.endswith(".zip")
    
    def validate(self, *args, **kwargs):
        # either a github repository is given or an archive
        print("\n\nin ModuleCreateForm.validate\n\n")
        r= super().validate(*args, **kwargs)
        print(f"\tvalidate val :  {r}")
        return r
    def process(self, *args, **kwargs):
        print("\n\nin ModuleCreateForm.process\n\n")
        print(args, kwargs)
        r=super().process(*args, **kwargs)
        print(f"\tprocess val : {r}")
        return r
 

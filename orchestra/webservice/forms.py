import os
import tempfile
import zipfile
import json

import werkzeug.datastructures

from flask import current_app, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms import validators

from .models import Module

class ModuleArchiveValidator(object):
    def __init__(self, extentions=[".zip"], message=None):
        self.extensions = extentions
        if not message:
            message = f"Input file must be one of the following type : {self.extensions}."
        self.message = message
    def __call__(self, form, field):
        extension = os.path.splitext(field.data.filename)[1]
        if not extension in self.extensions:
            raise validators.ValidationError(self.message+f" Got ({extension}).")

class OneOrTheOther(object):
    def __init__(self, fieldnames):
        self.fieldnames=fieldnames
    def __call__(self, form, field):
        fields = [form[f] for f in self.fieldnames]
        has_data = []
        for field in fields:
            if isinstance(field.data, str):
                has_data.append(len(field.data)>0)
            if isinstance(field.data, werkzeug.datastructures.FileStorage):
                has_data.append(len(field.data.filename)>0)
        print([f.data for f in fields])
        print("HHHHHHH", sum(has_data))
        if sum(has_data)!=1:
            raise validators.ValidationError("Please provide either a Github repository or an archive.")

def find_files(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            yield os.path.join(root, name)


class ModuleUniqueNameValidator(object):
    def __init__(self):
        self.message = "Module with name \"{}\" already exists."
    def __call__(self, form, field):
        # target filename 
        #target_filename = os.path.join(temp_dir, field.data.filename)
        if len(field.data.filename)==0:
            return
        target_filename = os.path.join(current_app.instance_path, "archive", field.data.filename)
        # save the archive
        field.data.save(target_filename)
        extensions = [".zip"]
        extension = os.path.splitext(target_filename)[1]
        if not extension in extensions:
            message = f"Input file must be one of the following type : {extensions}."
            raise validators.ValidationError(message+f" Got ({extension}).")

        with zipfile.ZipFile(target_filename, "r") as zip_ref:
            # create a temporary directory in which to unzip
            with tempfile.TemporaryDirectory() as temp_dir_zip:
                try:
                    zip_ref.extractall(temp_dir_zip)
                except zipfile.BadZipFile:
                    raise validators.ValidationError("Unable to read module archive.")
                # if metadata.json file does not exist raise a validation error
                # archive should contain at least one metadata.json file
                metadata_paths = list(find_files("metadata.json", temp_dir_zip))
                #metadata_path = os.path.join(temp_dir_zip, "metadata.json")
                #if not os.path.exists(metadata_path):
                if len(metadata_paths)==0:
                    raise validators.ValidationError("Module archive should contain a 'metadata.json' file.")
                # check names of modules
                for metadata_path in metadata_paths:
                    # read the metadata
                    metadata = json.load(open(metadata_path,"r"))
                    if not "name" in metadata:
                        raise validators.ValidationError("Invalid metadata.json file.")
                    # check that there are no installed modules with the same name
                    module_name = metadata["name"]
                    modules = Module.query.where(Module.name==module_name)
                    if modules.count():
                        raise validators.ValidationError(f"A Module named '{module_name}' already exists.")

 

class ModuleCreateForm(FlaskForm):
    #name = StringField("Module name", validators=[validators.Optional()])
    repository = StringField("Module Github repository", validators=[validators.Optional(),
        OneOrTheOther(["repository", "archive"]),
        validators.URL()])
    archive = FileField("Module archive", validators=[validators.Optional(),
    #    #ModuleArchiveValidator(),
        OneOrTheOther(["repository", "archive"]),
        ModuleUniqueNameValidator()])
    #json = StringField("JSON", validators=[validators.Optional()])
    #context_id = StringField("Context id", validators=[validators.Optional()])

    def process(self, *args, **kwargs):
        print("\n\nin ModuleCreateForm.process\n\n")
        print(args, kwargs)
        r=super().process(*args, **kwargs)
        print(f"\tprocess val : {r}")
        return r
 

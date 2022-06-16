import os
import zipfile
import tempfile
import json

from flask import redirect, url_for, request
import flask_login as login

from .models import Module
from .forms import ModuleCreateForm

# module info and manager
from .module.info import ModuleInfo
from .module.manager import ModuleManager
from orchestra.context.manager import ContextManager

# database
from .db import get_db


from flask import current_app
from flask_admin.contrib.sqla import ModelView

class ModuleView(ModelView):
    can_view_details = True
    column_display_pk = True
    column_sortable_list = None
    column_searchable_list = ("name",)
    edit_modal = True
    def is_accessible(self):
        return login.current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login", next=request.url))
    def create_form(self):
        form = ModuleCreateForm()
        return form
    def create_model(self, form):
        f = form["archive"].data
        filename = f.filename
        if len(filename):
            target_filename = os.path.join(current_app.instance_path, "archive", filename)
            f.save(target_filename)
            # unzip the file and register the module
            with zipfile.ZipFile(target_filename, "r") as zip_ref:
                # create a temporary directory in which to unzip
                with tempfile.TemporaryDirectory() as temp_dir:
                    zip_ref.extractall(temp_dir)
                    # register module
                    metadata_path = os.path.join(temp_dir, "metadata.json")
                    module_info = ModuleInfo(metadata_path)
                    mod_manager = ModuleManager()
                    json_data, context_id = mod_manager.register_module(module_info)
                    # save a new Module object to the database
                    mod = Module(name=json_data["name"], json=json.dumps(json_data), context_id=context_id)
                    db = get_db()
                    db.session.add(mod)
                    db.session.commit()
                    return mod
        # github repository
        github_repo = form["repository"].data
        if len(github_repo):
            current_dir = os.getcwd()
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)
                os.system(f"git clone -c http.sslVerify=0 {github_repo}")
                repository_folder = os.path.basename(github_repo).replace(".git", "")
                metadata_path = os.path.join(repository_folder, "metadata.json")
                mod_manager = ModuleManager()
                module_info = ModuleInfo(metadata_path)
                json_data, context_id = mod_manager.register_module(module_info)
                mod = Module(name=json_data["name"], json=json.dumps(json_data), context_id=context_id)
                db = get_db()
                db.session.add(mod)
                db.session.commit()
                os.chdir(current_dir)
                return mod
        r = super().create_model(form)
        return r
    def after_model_delete(self, model):
        # delete the context
        ContextManager().remove(model.context_id)

class TaskView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login", next=request.url))
 

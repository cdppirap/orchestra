import os
import zipfile
import tempfile
import json

from .models import Module
from .forms import ModuleCreateForm

# module info and manager
from .module.info import ModuleInfo
from .module.manager import ModuleManager

# database
from .db import get_db


from flask import current_app
from flask_admin.contrib.sqla import ModelView

class ModuleView(ModelView):
    def create_form(self):
        form = ModuleCreateForm()
        return form
    def create_model(self, form):
        print("\n\nin ModuleView.create_model\n\n")
        print(f"\tname : {form['name'].data}")
        print(f"\tfile : {form['archive'].data}")
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
            print(f"current dir : {current_dir}")
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)
                os.system(f"git clone -c http.sslVerify=0 {github_repo}")
                repository_folder = os.path.basename(github_repo).replace(".git", "")
                metadata_path = os.path.join(repository_folder, "metadata.json")
                mod_manager = ModuleManager()
                module_info = ModuleInfo(metadata_path)
                json_data, context_id = mod_manager.register_module(module_info)
                print("JSON data : ", json_data, context_id)
                mod = Module(name=json_data["name"], json=json.dumps(json_data), context_id=context_id)
                db = get_db()
                db.session.add(mod)
                db.session.commit()
                os.chdir(current_dir)
                return mod





            
        r = super().create_model(form)
        print(f"\tcreate_model returns : {r}")
        return r

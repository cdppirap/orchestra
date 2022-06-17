import os
import zipfile
import tempfile
import json
import urllib

from flask import redirect, url_for, request
import flask_login as login

from .models import Module, Task
from .forms import ModuleCreateForm

# module info and manager
from .module.info import ModuleInfo
from .module.manager import ModuleManager
from orchestra.context.manager import ContextManager

# database
from .db import get_db


from flask import current_app
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin import BaseView, expose

class ModuleView(ModelView):
    can_view_details = True
    column_display_pk = True
    column_sortable_list = None
    column_searchable_list = ("name",)
    edit_modal = True

    # added test action
    column_extra_row_actions = [
            EndpointLinkRowAction("glyphicon glyphicon-play", ".test_view", "Run module with defaults"),
            ]
    @expose("/test", methods=("GET",))
    def test_view(self):
        module_id = request.args["id"]
        mod = Module.query.get(module_id)
        run_url = url_for("runmodule", module_id=module_id,**json.loads(mod.default_args), _external=True)
        with urllib.request.urlopen(run_url) as f:
            task_data = json.loads(f.read().decode("utf8"))
            print(task_data)
            return redirect(url_for("task.details_view", id=task_data["task"]))

        return redirect(url_for(".index_view"))

    def is_accessible(self):
        return login.current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        #return redirect(url_for("login", next=request.url))
        return redirect(url_for("admin.login_view", next=request.url))

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
                    mod = Module(context_id=context_id)
                    mod.load_json(json_data)
                    #mod = Module(name=json_data["name"], json=json.dumps(json_data), context_id=context_id)
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
                mod = Module(context_id=context_id)
                mod.load_json(json_data)
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
    can_view_details = True
    column_display_pk = True
    column_sortable_list = None
    column_searchable_list = ("status", "module_id",)
    #column_select_related_list = ("module_id",)
    can_create = False
    can_edit = False
    details_modal = False
    details_template = "task/details.html"
    # added output download action
    column_extra_row_actions = [
            EndpointLinkRowAction("glyphicon glyphicon-download-alt", ".output_view", "Download task output"),
            ]
    @expose("/output", methods=("GET",))
    def output_view(self):
        print(current_app.url_map)
        task_id = request.args["id"]
        task = Task.query.get(task_id)
        run_url = url_for("taskoutput", task_id=task_id, _external=True)
        return redirect(run_url)


    def is_accessible(self):
        return login.current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin.login_view", next=request.url))
 

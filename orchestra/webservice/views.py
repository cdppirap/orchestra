import os
import io
import json
import urllib
import uuid
from datetime import datetime

from jinja2.utils import markupsafe

from flask import redirect, url_for, request, flash, send_file
import flask_login as login
import flask_admin
from flask_admin.actions import action
from flask_admin.babel import gettext, ngettext

from .models import Module, Task, ModuleInfo
from .forms import ModuleCreateForm

# module info and manager
from .module.info import ModuleInstallationInfo
from .module.manager import ModuleManager
from orchestra.context.manager import ContextManager

# validators
from .validators import StringListValidator, ModuleArgumentDefaultsValidator, PythonVersionValidator, ModuleOutputValidator, JSONValidator

# database
from .db import get_db

# celery tasks
from . import tasks

# configuration
from orchestra import configuration as config

from flask import current_app
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin import BaseView, expose

from wtforms import SelectField

class ModuleRunDefaultsAction(EndpointLinkRowAction):
    def __init__(self):
        super().__init__("glyphicon glyphicon-play", ".test_view", "Run module with defaults")
class ModuleReinstallAction(EndpointLinkRowAction):
    def __init__(self):
        super().__init__("glyphicon glyphicon-refresh", ".reinstall_view", "Reinstall")

class TaskDeleteAction(EndpointLinkRowAction):
    def __init__(self):
        super().__init__("glyphicon glyphicon-trash", ".delete_view", "Delete task")
class TaskDownloadOutputAction(EndpointLinkRowAction):
    def __init__(self):
        super().__init__("glyphicon glyphicon-download-alt", ".output_view", "Download task output")
class TaskKillAction(EndpointLinkRowAction):
    def __init__(self):
        super().__init__("glyphicon glyphicon-stop", ".kill_view", "Kill task")







class ModuleView(ModelView):
    can_view_details = True
    column_display_pk = True
    column_sortable_list = None
    column_searchable_list = ("name","status",)
    edit_modal = True
    details_template = "module/details.html"
    list_template = "module/list.html"
    can_set_page_size = True
    column_exclude_list = ("build_log","arguments","hyperparameters","default_args","install",
            "context_id", "output", "requirements_file","files","install_source", "post_process", "pre_process")

    form_overrides = {
            "status": SelectField,
            }
    form_args = {
            "arguments": {
                "validators": [JSONValidator(),
                    StringListValidator()],
                },
            "hyperparameters": {
                "validators": [JSONValidator(),
                    StringListValidator()],
                },
            "default_args": {
                "validators": [JSONValidator(),
                    ModuleArgumentDefaultsValidator()],
                },
            "python_version":{
                "validators": [PythonVersionValidator()],
                },
            "requirements":{
                "validators": [JSONValidator(),
                    StringListValidator()],
                },
            "files": {
                "validators": [JSONValidator(),
                    StringListValidator()],
                },
            "pre_process": {
                "validators": [JSONValidator(),
                    StringListValidator()],
                },
            "post_process": {
                "validators": [JSONValidator(),
                    StringListValidator()],
                },
            "output": {
                "validators": [JSONValidator(), ModuleOutputValidator()],
                },

            "status": {"choices":["installed", "error", "pending"]},
            }

    form_excluded_columns = ("build_log",)

    def description_formatter(view, context, model, name):
        if model.description is None:
            return ""
        if len(model.description)<30:
            return model.description
        return model.description[:27] + "..."
    def requirements_formatter(view, context, model, name):
        if model.requirements is None:
            return 0
        return len(json.loads(model.requirements))
    column_formatters = {
            "description": description_formatter,
            "requirements": requirements_formatter,
            }
    column_formatters_detail = {
            "description": None,
            "requirements": None,
            }

    @action("reinstall", "Reinstall", "Are you sure you want to reinstall the selected Modules ?")
    def action_reinstall(self, ids):
        if len(ids):
            for i in ids:
                mod = Module.query.get(i)
                if mod.status=="pending":
                    flash(markupsafe.Markup(f"Cannot reinstall {mod.details_link()} with 'pending' status."), "error")
                else: 
                    tasks.reinstall_module.delay(i)
                    flash(markupsafe.Markup(f"Reinstalling {mod.details_link()}."), "success")
        return redirect(url_for(".index_view"))
    @action("run_defaults", "Run defaults")
    def action_run_defaults(self, ids):
        # find ids of modules with pending status
        if len(ids):
            manager = ModuleManager()
            for i in ids:
                mod = Module.query.get(i)
                if mod.status in ["error", "pending"]:
                    flash(markupsafe.Markup(f"Cannot run module {mod.details_link()} with status '{mod.status}'."), "error")
                else:
                    args = json.loads(mod.default_args)
                    task_id=manager.start_task(i, args)
                    tasks.run_module.delay({"task_id":task_id, "args": args})
                    task = Task.query.get(task_id)
                    flash(markupsafe.Markup(f"Created {task.details_link()} for {mod.details_link()}."), "success")

        return redirect(url_for(".index_view"))


    # added test action
    column_extra_row_actions = [
            ModuleRunDefaultsAction(),
            ModuleReinstallAction(),
            #EndpointLinkRowAction("glyphicon glyphicon-play", ".test_view", "Run module with defaults"),
            #EndpointLinkRowAction("glyphicon glyphicon-refresh", ".reinstall_view", "Reinstall"),

            ]

    # action permissions based on status
    def allow_row_action(self, action, model):
        print("ACTION : ", action)
        if isinstance(action, flask_admin.model.template.ViewRowAction):
            return True
        if isinstance(action, flask_admin.model.template.EditPopupRowAction):
            return True
        if isinstance(action, flask_admin.model.template.DeleteRowAction):
            return True
        if isinstance(action, ModuleRunDefaultsAction):
            return model.status == "installed"
        if isinstance(action, ModuleReinstallAction):
            return model.status in ["error", "installed"]
        return True
    @expose("/test", methods=("GET",))
    def test_view(self):
        module_id = request.args["id"]
        mod = Module.query.get(module_id)
        if mod.status != "installed":
            flash("Cannot run a module that is not installed.", "error")
            return redirect(url_for(".index_view"))
        run_url = url_for("runmodule", module_id=module_id,**json.loads(mod.default_args), _external=True)
        with urllib.request.urlopen(run_url) as f:
            task_data = json.loads(f.read().decode("utf8"))
            return redirect(url_for("task.details_view", id=task_data["task"]))

        return redirect(url_for(".index_view"))
    @expose("/dockerfile", methods=("GET",))
    def dockerfile_view(self):
        module_id = request.args["id"]
        module = Module.query.get(module_id)
        module_info = module.info()
        context = module_info.get_context()
        dockerfile = context.to_dockerfile()
        return send_file(dockerfile, as_attachment=True, attachment_filename=f"{module.name}.docker", mimetype="text/txt")
    @expose("/requirements", methods=("GET",))
    def requirements_view(self):
        module_id = request.args["id"]
        module = Module.query.get(module_id)
        f = io.BytesIO("\n".join(json.loads(module.requirements)).encode())
        return send_file(f, as_attachment=True, attachment_filename="requirements.txt", mimetype="text/txt")
    @expose("/metadata", methods=("GET",))
    def metadata_view(self):
        module_id = request.args["id"]
        module = Module.query.get(module_id)
        f = io.BytesIO(json.dumps(module.to_json(), indent=4).encode())
        return send_file(f, as_attachment=True, attachment_filename="metadata.json", mimetype="text/txt")
    @expose("/reinstall", methods=("GET",))
    def reinstall_view(self):
        db = get_db()
        module_id = request.args["id"]
        module = Module.query.get(module_id)
        module.build_log = ""
        module.status = "pending"

        db.session.commit()
        
        tasks.reinstall_module.delay(module.id)
        return redirect(url_for("module.details_view", id=module_id))

    def is_accessible(self):
        return login.current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        #return redirect(url_for("login", next=request.url))
        return redirect(url_for("admin.login_view", next=request.url))

    def create_form(self):
        form = ModuleCreateForm()
        return form
    def create_model(self, form):
        """Create the new Module object, form data should have been validated at this point.
        A new empty Module object is created with a pending status. The registration process
        will update its status to installed or error after building the execution context.
        """
        # database connection
        db = get_db()
        # add a pending Module object
        temp_name = "TempModule_" + uuid.uuid4().hex[:4].upper()
        new_mod = Module(status="pending", name=temp_name)
        # save the new Module
        db.session.add(new_mod)
        db.session.commit()
        db.session.refresh(new_mod)
        # at this point the Module object should have a new id

        # create the ModuleInstallationInfo object and pass it to the ModuleManager object for registration
        f = form["archive"].data
        filename = f.filename
        if len(filename):
            # an archive containing the module data was passed in the form, the file has already been saved by the validation process
            #target_filename = os.path.join(current_app.instance_path, "archive", filename)
            target_filename = os.path.join(config.archive_directory, filename)
            #f.save(target_filename)
            # create the ModuleInstallationInfo object
            module_install = ModuleInstallationInfo(module_id=new_mod.id,
                    filename=target_filename)
            # launch registration task
            print(module_install.to_json(), type(module_install.to_json()))
            tasks.register_module.delay(module_install.to_json())
            return new_mod

           
        # github repository
        github_repo = form["repository"].data
        if len(github_repo):
            print("\nRegister from Git\n")
            # module information is in a github repository
            module_install = ModuleInstallationInfo(module_id=new_mod.id,
                    git=github_repo)

            # launch registration task
            tasks.register_module.delay(module_install.to_json())
            return new_mod

        r = super().create_model(form)
        return r

    def after_model_delete(self, model):
        # delete the context
        ContextManager().remove(model.context_id)

class TaskView(ModelView):
    page_size = 20
    can_delete = False
    can_set_page_size = True
    can_view_details = True
    column_display_pk = True
    column_sortable_list = None
    column_searchable_list = ("status", "module_id",)
    #column_select_related_list = ("module_id",)
    can_create = False
    can_edit = False
    details_modal = False
    details_template = "task/details.html"
    column_exclude_list = ("celery_id", "execution_log","output_dir","command")
    form_excluded_columns = ("celery_id", "execution_log", "output_dir",)
    # added output download action
    column_extra_row_actions = [
            TaskDeleteAction(),
            TaskDownloadOutputAction(),
            TaskKillAction(),
            #EndpointLinkRowAction("glyphicon glyphicon-trash", ".delete_view", "Delete task"),
            #EndpointLinkRowAction("glyphicon glyphicon-download-alt", ".output_view", "Download task output"),
            #EndpointLinkRowAction("glyphicon glyphicon-remove", ".kill_view", "Kill task"),
            ]
    list_template="task/list.html"
    def allow_row_action(self, action, model):
        print("TASK ACTION : ", action)
        if isinstance(action, TaskDeleteAction):
            return True
        if isinstance(action, TaskDownloadOutputAction):
            return model.status == "done"
        if isinstance(action, TaskKillAction):
            return model.status == "running"
        return True

    def start_formatter(view, context, model, name):
        return datetime.fromtimestamp(model.start).strftime("%Y-%m-%d %H:%M:%S.%f")
    def stop_formatter(view, context, model, name):
        if model.stop:
            return datetime.fromtimestamp(model.stop).strftime("%Y-%m-%d %H:%M:%S.%f")
        return ""
    def module_id_formatter(view, context, model, name):
        if model.module_id:
            return markupsafe.Markup(f"<a href=\"{url_for('module.details_view', id=model.module_id)}\">{model.module}</a>")
        return "Module deleted"

    column_formatters = {"start": start_formatter,
            "stop": stop_formatter,
            "module_id": module_id_formatter,
            "module": module_id_formatter,

            }



    @expose("/kill", methods=("GET",))
    def kill_view(self):
        task_id = request.args["id"]
        task = Task.query.get(task_id)
        if task.status in ["done", "terminated"]:
            flash(f"Task {task.id} is not running and cannot be killed.")
        else:
            run_url = url_for("killtask", task_id=task_id, _external=True)
            with urllib.request.urlopen(run_url) as f:
                task_data = json.loads(f.read().decode("utf8"))
                return redirect(url_for("task.details_view", id=task_id))

        return redirect(url_for("task.index_view"))

    @expose("/delete_task", methods=("GET",))
    def delete_view(self):
        task_id = request.args["id"]
        task = Task.query.get(task_id)
        if task.status in ["done", "terminated", "error"]:
            super().delete_model(task)
            flash(gettext('Task was successfully deleted.'), 'success')

            #flash(f"Task {task.id} is not running and cannot be killed.")
        else:
            flash(gettext('Cannot delete a running task. Terminate it or wait until task is done.'), 'error')
        return redirect(url_for("task.index_view"))


    @expose("/output", methods=("GET",))
    def output_view(self):
        task_id = request.args["id"]
        task = Task.query.get(task_id)
        if task.status=="terminated":
            flash("Cannot download output for terminated Task {task.id}.", "error")
            return redirect(url_for(".index_view"))
        if task.status=="error":
            flash("Cannot download output for Task {task.id} that terminated with errors.", "error")
            return redirect(url_for(".index_view"))
        if task.status=="running":
            flash("Cannot download output for Task {task.id} that is running.", "error")
            return redirect(url_for(".index_view"))

        run_url = url_for("taskoutput", task_id=task_id, _external=True)
        return redirect(run_url)


    def is_accessible(self):
        return login.current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin.login_view", next=request.url))
    def after_model_delete(self, model):
        # delete the context
        ModuleManager().remove_task(model.id)

 

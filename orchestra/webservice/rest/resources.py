import os
import json
import time

from flask import Flask, request, send_from_directory, redirect, Response
from flask_restful import Resource, Api, reqparse
from flask_admin import Admin, AdminIndexView
from werkzeug.exceptions import HTTPException

from ..models import Task, Module
from ..db import get_db

from ..module.info import ModuleInfo
from ..module.manager import ModuleManager

import orchestra.configuration as config

from .. import tasks as _tasks

manager = ModuleManager()


class ListModules(Resource):
    """Module list endpoint, inquiring this endpoint will return a list of (id, name) pairs for every
    module that is currently registered
    """
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("debug", type=bool, default=False, location="args")
        args = parser.parse_args()

        return [{"id":k, "name":m.metadata["name"]} for k,m in manager.iter_modules(debug=args.debug)]
 
class ShowModule(Resource):
    """Get module information
    """
    def get(self, module_id):
        module_id = int(module_id)
        if not int(module_id) in manager:
            return {"error":"Module does not exist"}
        module = manager[module_id]
        return module.metadata

class RunModule(Resource):
    """Run a module
    """
    def get_run_arguments(self, module_id):
        parser = reqparse.RequestParser()
        # list of arguments in module
        module = manager[module_id]
        # add arguments to parser
        argument_keys = module.metadata["args"]
        argument_keys += module.metadata["hyperparameters"]
        if not "start" in argument_keys:
            argument_keys.append("start")
        if not "stop" in argument_keys:
            argument_keys.append("stop")
        for k in argument_keys:
            if isinstance(k, str):
                parser.add_argument(k, type=str, location="args")
            if isinstance(k, tuple) or isinstance(k, list):
                parser.add_argument(k[0], type=eval(k[1]), location="args")

        args = parser.parse_args()

        print("Module arguments :\n{}".format(json.dumps(args, indent=4, sort_keys=True)))
        return args

    def get(self, module_id):
        module_id = int(module_id)
        if not module_id in manager:
            return {"error":"Module does not exist"}
        # arguments
        run_arguments = self.get_run_arguments(module_id)
        # start a run task with the manager
        task_id=manager.start_task(module_id, run_arguments)
        _tasks.run_module.delay({"task_id":task_id, "args": run_arguments})
        return {"status":"running", "task":task_id}

class ListTasks(Resource):
    """List task information
    """
    def get(self):
        return [tid for tid,_ in manager.iter_tasks()]
    def post(self):
        return self.get()

class ShowTask(Resource):
    """Get task information
    """
    def get_task_status(self, task_id):
        task=manager.get_task(task_id)
        task_dir = manager.get_task_dir(task_id)
        exitcode = task.exitcode
        if exitcode is None:
            return "running"
        if exitcode == 0:
            if "error.log" in list(os.listdir(task_dir)):
                emsg = self.read_error_log(task_id)
                if len(emsg):
                    return "error"
            return "done"
        return "error"
    def get_output_files(self, task_id):
        task_dir = manager.get_task_dir(task_id)
        a=list(os.listdir(task_dir))
        if "error.log" in a:
            if os.path.getsize(os.path.join(manager.get_task_dir(task_id), "error.log"))==0:
                a.remove("error.log")
        return a
    def read_error_log(self, task_id):
        r=None
        task_dir = manager.get_task_dir(task_id)
        error_file = os.path.join(task_dir, "error.log")
        if not os.path.exists(error_file):
            return ""
        with open(error_file, "r") as f:
            r=f.read()
        return r
    def get(self, task_id):
        if not manager.has_task(task_id):
            return {"error":"Task {} not found".format(task_id)}
        # status flag
        tid = int(task_id)
        task = manager.get_task(tid)
        if task.is_done():
            task.data["output"]=self.get_output_files(tid)
        return task.data

        exitcode = manager.get_task(tid).exitcode
        task_status = self.get_task_status(tid)
        error=None
        if task_status!="done":
            output = None
            if task_status=="error":
                error = self.read_error_log(tid)
        else:
            output = self.get_output_files(tid)
            output = [o for o in output if o!="error.log"]

        return {"status":task_status,\
                "output":output,\
                "error":error,\
                "id":int(task_id)}

class KillTask(Resource):
    """Kill a task by id
    """
    def get(self, task_id):
        manager.kill_task(int(task_id))
        task = Task.query.get(task_id)
        task.celery_id = None
        task.status = "terminated"
        task.stop = time.time()
        get_db().session.commit()
        return {}
    def post(self, task_id):
        return self.get(task_id)

class TaskOutput(Resource):
    """Get task output files
    """
    def get(self, task_id):
        task = manager.get_task(task_id)
        if task.is_done():
            # get the module
            #module = Module.query.get(task.get_module_id()).info()
            module = manager[task.get_module_id()]
            # only return output if task is done
            output_dir = task["output_dir"]
            # get the output filenames
            print(module.metadata)
            output_filenames = module.get_output_filenames()
            output_files = list(os.listdir(output_dir))

            # if no error.log file or if it is empty then remove it
            if "error.log" in output_files:
                # get error log size
                if os.path.getsize(os.path.join(output_dir, "error.log"))==0:
                    output_files.remove("error.log")
            output_files = [of for of in output_files if of in output_filenames or of=="error.log"]
            if len(output_files)==1:
                return send_from_directory(output_dir, output_files[0], as_attachment=False)
            if len(output_files)>1:
                # create a temporary directory
                prev_dir = os.getcwd()
                with tempfile.TemporaryDirectory() as tempdir:
                    #os.chdir(tempdir)
                    # zip the files
                    os.system(f"zip {tempdir}/output.zip {' '.join(output_files)}")
                    return send_from_directory(output_dir, os.path.join(tempdir,"output.zip"), as_attachment=False)
                ## zip the output
                #cmd = "cd {} ; zip output.zip {}".format(output_dir, " ".join(output_files))
                #os.system(cmd)
                #r=send_from_directory(output_dir, "output.zip", as_attachment=False)
                #os.system("rm -rf {}/output.zip".format(output_dir))
                return r
        return None



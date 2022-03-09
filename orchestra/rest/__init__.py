"""Orchestra REST API

Endpoints : - modules : list of installed modules
            - modules/<module_id> : module information
            - modules/<module_id>/run : run the module
            - modules/<module_id>/train : train the module

"""
import os
import json

from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api, reqparse

from orchestra.module.info import ModuleInfo
from orchestra.module.manager import ModuleManager

import orchestra.configuration as config

manager = ModuleManager()

app = Flask(__name__)
api = Api(app)



class ListModules(Resource):
    """Module list endpoint, inquiring this endpoint will return a list of (id, name) pairs for every
    module that is currently registered
    """
    def get(self):
        #manager = ModuleManager()
        return [{"id":k, "name":m.metadata["name"]} for k,m in manager.iter_modules()]
 
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
        argument_keys = module.metadata["args"]+["start", "stop"]
        for k in argument_keys:
            parser.add_argument(k, type=str)

        args = parser.parse_args()

        print("Module arguments :\n{}".format(json.dumps(args, indent=4, sort_keys=True)))
        #print("ARgs : {}".format(args))
        return args

    def get(self, module_id):
        module_id = int(module_id)
        if not module_id in manager:
            return {"error":"Module does not exist"}
        # arguments
        run_arguments = self.get_run_arguments(module_id)
        # start a run task with the manager
        task_id=manager.start_task(module_id, **run_arguments)
        return {"status":"running", "task":task_id}
    def put(self, module_id):
        return self.get(module_id)

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
        return {}
    def post(self, task_id):
        return self.get(task_id)

class TaskOutput(Resource):
    """Get task output files
    """
    def get(self, task_id):
        task = manager.get_task(task_id)
        if task.is_done():
            output_dir = task["output_dir"]
            #output_dir = manager.get_task_dir(task_id)
            #output_dir = os.path.abspath(output_dir)
            output_files = list(os.listdir(output_dir))
            if "error.log" in output_files:
                # get error log size
                if os.path.getsize(os.path.join(output_dir, "error.log"))==0:
                    output_files.remove("error.log")
            if len(output_files)==1:
                content = open(os.path.join(output_dir,output_files[0]), "rb").read().decode("utf-8")
                return send_from_directory(output_dir, output_files[0], as_attachment=True)
            if len(output_files)>1:
                # zip the output
                cmd = "cd {} ; zip output.zip {}".format(output_dir, " ".join(output_files))
                os.system(cmd)
                r=send_from_directory(output_dir, "output.zip", as_attachment=True)
                os.system("rm -rf {}/output.zip".format(output_dir))
                return r
        return None

# module related 
api.add_resource(ListModules, "/modules")
api.add_resource(ShowModule, "/modules/<string:module_id>")
api.add_resource(RunModule, "/modules/<string:module_id>/run")

# task related
api.add_resource(ListTasks,"/tasks")
api.add_resource(ShowTask, "/tasks/<int:task_id>")
api.add_resource(KillTask, "/tasks/<int:task_id>/kill")
api.add_resource(TaskOutput, "/tasks/<int:task_id>/output")



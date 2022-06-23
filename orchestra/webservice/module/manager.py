import os
import sys
import time
import json
import sqlite3
import pickle as pkl
from multiprocessing import Process
import subprocess

# database
from ..db import get_db
from ..models import Module, Task

from ..module.info import ModuleInfo

from orchestra.errors import ModuleIDNotFound
from orchestra.environment import ModuleEnvironment

from orchestra.context.manager import ContextManager
from ..task.info import TaskInfo, TaskStatus



import orchestra.configuration as config

class ModuleManager:
    """Class for managing a collection of Module objects, start and stop tasks and more.
    """
    def __init__(self):
        self.task_counter = 0
        self.tasks={}
        self.create_task_output_dir()
   
    def clear_contexts(self):
        """Delete all contexts
        """
        cmanager = ContextManager()
        for mid,m in self.iter_modules():
            context_id = self.get_context_id(mid)
            cmanager.remove(context_id)
    def clear(self):
        """Clear the list of modules and all associated tasks
        """
        # clear contexts
        self.clear_contexts()

        sql = "DELETE FROM {}".format(config.module_info_table)
        self.execute_sql(sql)
        self.execute_sql("DELETE FROM {}".format(config.task_info_table))
        # clear tasks
        self.clear_tasks()

        # prune docker images and containers
        ContextManager().docker_prune()


    def clear_tasks(self):
        """Clear list of tasks
        """
        self.tasks = {}
        # remove all task outputs 
        os.system("rm -rf {}".format(os.path.join(config.task_directory,"*")))

    def iter_modules(self, status="installed"):
        """Module iterator, yields tuples (module_id, module_obj)
        """
        modules = Module.query.where(Module.status == status)
        for module in modules:
            yield module.id, module.info()
        
    def iter_tasks(self):
        """Task iterator, yields tuples (module_id, module_obj)
        """
        tasks = Task.query.all()
        for task in tasks:
            yield task.id, task.info()


    def module_from_row(self, row):
        """Create a ModuleInfo object from a row of the module info table
        """
        module_id = int(row[0])
        return ModuleInfo.from_json(row[1])

    def __contains__(self, module_id):
        """Check if a module is installed, the input can be either the modules id or a ModuleInfo object
        """
        return Module.query.get(module_id) is not None

    def __len__(self):
        """Get number of installed modules
        """
        return Module.query.count()
        sql = "SELECT count(id) FROM {}".format(config.module_info_table)
        conn = self.get_database_connection()
        cursor = conn.cursor()
        ans = [r for r in cursor.execute(sql)]
        conn.close()
        n=int(ans[0][0])
        return n
    def get_database_connection(self):
        """Get connection to the module info database
        """
        return sqlite3.connect(config.database)

    def register_module(self, module, verbose=True):
        """Register a module, returns the module id
        """
        if verbose:
            sys.stdout.write("Registrating {}...".format(module))
            sys.stdout.flush()
        # create the context
        image_tag = "orchestra:{}".format(module.metadata["name"])
        context = module.get_context()
        context = ContextManager().build(context, tag = image_tag)

        module.metadata["build_log"] = context["log"]
        if "error" in context:
            # set the metadata
            module.metadata["status"] = "error"
            return module.metadata, None

        image = context["image"]

        return module.metadata, image.id

       
    def __getitem__(self, module_id):
        """Get a ModuleInfo object by id
        """
        return Module.query.get(module_id).info()

    def remove_module(self, module_id):
        """Remove a module
        """
        print(f"Remove moduel {module_id}")
        # delete related contexts first
        context_id = self.get_context_id(module_id)
        ContextManager().remove(context_id)


        sql = "DELETE FROM {} WHERE id={}".format(config.module_info_table, module_id)
        conn = self.get_database_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()


    def forcefully_remove_directory(self, path):
        """Forcefully remove a directory
        """
        cmd = "rm -rf {}".format(path)
        #cmd = "rm -rf {} &> /dev/null".format(path)
        os.system(cmd)
    def create_task_output_dir(self):
        """Create task output directory if needed
        """
        if not os.path.exists(config.task_directory):
            os.makedirs(config.task_directory, exist_ok=True)
            os.system("chmod a+s {}".format(config.task_directory))
    def get_task_dir(self, task_id):
        """Get path of a task directory
        """
        return os.path.join(config.task_directory, "task_{}".format(task_id))
    def get_task_info_insert_query(self, task):
        return "INSERT INTO {} (json) VALUES (\'{}\');".format(config.task_info_table,
                json.dumps(task.data))
    def get_task_info_update_query(self, task):
        return "UPDATE {} SET json=\'{}\' WHERE id={};".format(config.task_info_table,
                json.dumps(task.data),
                task.id)
    def save_task(self, task):
        """Save a task, if it doesn't have an id yet then return one, else update
        """
        db = get_db()
        if task.id is None:
            # create new task object
            t = Task()
            t.load_json(task.data)
            db.session.add(t)
            db.session.flush()
            db.session.refresh(t)
            task.id = t.id
        else:
            t = Task.query.get(task.id)
            t.load_json(task.data)
        db.session.commit()
        return task.id



    def create_task_dir(self, task_id):
        """Create the task output directory, if the folder exists it is forcefully removed and
        a new folder is created with the same name
        """
        od = self.get_task_dir(task_id)
        if os.path.exists(od):
            self.forcefully_remove_directory(od)
        os.mkdir(od)
        os.system("chmod a+s {}".format(od))
        return os.path.abspath(od)

    def clean_tasks(self):
        """Remove all process objects that have finished running
        """
        self.tasks={k:self.tasks[k] for k in self.tasks if self.tasks[k].exitcode is None}

    def start_task(self, module_id, task_args):
        """Start a task for a module with the given arguments. All results of the execution are saved
        in a task directory. The id of the task is returned.
        """
        if not module_id in self:
            raise ModuleIDNotFound(module_id)

        # initiate a empty task object
        task = TaskInfo(module_id, task_args)
        task_id = self.save_task(task)
        task["id"]=task_id

        # create a temporary directory for storing the output of the run
        task["output_dir"] = self.create_task_dir(task_id)

        # clean task list
        #self.clean_tasks()
        
        # start the process
        #process = Process(target = self.run_module, args = (task,))
        #self.tasks[task_id]=process
        #self.tasks[task_id].start()

        self.save_task(task)

        return task_id

    def get_context_id(self, module_id):
        """Get a  module's context id
        """
        return Module.query.get(module_id).context_id

    def run_module(self, task, verbose=False):
        """This function is called by the process in charge of executing the module. Code is executed
        in a new process
        """
        if verbose:
            print("Request run for module id={}, args={}".format(module_id, task["arguments"]))
        # retrieve the module object
        module_id = task["module_id"]
        module = Module.query.get(module_id).info() #self[module_id]
        # the module's execution context
        print(f"Getting context id for module : {module_id}")
        context_id = self.get_context_id(module_id)
        print(f"Got context_id : {context_id}")
        # get the command line to send to the container
        command = module.get_cli_command("/output", task["arguments"])
        task["cmd"] = command
        # output directory
        output_dir = task["output_dir"]

        # TODO : add error and stdout handeling
        out = None

        task["start"] = time.time()
        self.save_task(task)
        result = ContextManager().run(context_id, command, output_dir)
        if "error" in result:
            task["status"] = TaskStatus.ERROR
        else:
            task["status"] = TaskStatus.DONE

        task["execution_log"] = result["log"]
        print("Log type ", type(result["log"]))

        # terminate the task at this point
        task["stop"]=time.time()
        task["celery_id"] = None
        self.save_task(task)
        return 

    def has_task(self, task_id):
        """Check if a task exists by id
        """
        tid = int(task_id)
        r=tid in [t.id for t in self.list_tasks()]
        return r
    def list_tasks(self):
        """Return list of tasks
        """
        return [t for _,t in self.iter_tasks()]
    def get_task(self, task_id):
        """Get task information
        """
        return Task.query.get(task_id).info()

    def kill_task(self, task_id):
        """Kill a task
        """
        task = Task.query.get(task_id)
        if task.celery_id:
            from celery import current_app
            current_app.control.revoke(task.celery_id, terminate=True)
        task_output_path = os.path.join(config.task_directory, "task_{}".format(task_id))
        self.forcefully_remove_directory(task_output_path)
    def remove_task(self, task_id):
        """Remove a task directory, the task should be done
        """
        self.forcefully_remove_directory(self.get_task_dir(task_id))
    def context_exists(self, context_id):
        """Check that context exists
        """
        return ContextManager().context_exists(context_id)


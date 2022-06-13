import os
import sys
import time
import json
import sqlite3
import pickle as pkl
from multiprocessing import Process
import subprocess

from orchestra.module.info import ModuleInfo
from orchestra.errors import ModuleIDNotFound
from orchestra.environment import ModuleEnvironment

from orchestra.context.manager import ContextManager
from orchestra.tasks.info import TaskInfo, TaskStatus

import orchestra.configuration as config

class ModuleManager:
    """Class for managing a collection of Module objects, start and stop tasks and more.
    """
    def __init__(self):
        self.init_database()
        self.task_counter = 0
        self.tasks={}
        self.create_task_output_dir()
    def create_module_info_table_query(self):
        """Create the module info table
        """
        return "CREATE TABLE IF NOT EXISTS {} (id integer PRIMARY KEY, json TEXT NOT NULL, context_id TEXT NOT NULL);".format(
                config.module_info_table)
    def create_task_info_table_query(self):
        """Create the task table query
        """
        return "CREATE TABLE IF NOT EXISTS {} (id integer PRIMARY KEY, json TEXT NOT NULL);".format(
                config.task_info_table)
    def execute_sql(self, query):
        """Execute an SQL query that has not result
        """
        #print("EXEC : {}".format(query))
        lastrowid=None
        conn = sqlite3.connect(config.database)
        cursor = conn.cursor()
        cursor.execute(query)
        if query.startswith("INSERT"):
            lastrowid = cursor.lastrowid
        conn.commit()
        conn.close()
        return lastrowid
 
    def init_database(self):
        """Inialize the database, create the module info table
        """
        conn = self.get_database_connection()
        # create tables if they do not exist
        self.execute_sql(self.create_module_info_table_query())
        self.execute_sql(self.create_task_info_table_query())
    
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

    def iter_modules(self):
        """Module iterator, yields tuples (module_id, module_obj)
        """
        sql = "SELECT * FROM {} ORDER BY id".format(config.module_info_table)
        conn = sqlite3.connect(config.database)
        cursor = conn.cursor()
        for row in cursor.execute(sql):
            yield int(row[0]),ModuleInfo.from_json(row[1])
        conn.commit()
        conn.close()

    def iter_tasks(self):
        """Task iterator, yields tuples (module_id, module_obj)
        """
        sql = "SELECT * FROM {} ORDER BY id".format(config.task_info_table)
        conn = sqlite3.connect(config.database)
        cursor = conn.cursor()
        for row in cursor.execute(sql):
            yield int(row[0]),TaskInfo.from_json(row[1])
        conn.commit()
        conn.close()



    def module_from_row(self, row):
        """Create a ModuleInfo object from a row of the module info table
        """
        module_id = int(row[0])
        return ModuleInfo.from_json(row[1])

    def __contains__(self, module_id):
        """Check if a module is installed, the input can be either the modules id or a ModuleInfo object
        """
        sql = "SELECT * FROM {} WHERE id={}".format(config.module_info_table, module_id)
        conn = self.get_database_connection()
        cursor = conn.cursor()
        ans = [r for r in cursor.execute(sql)]
        conn.close()
        return len(ans)>0

    def __len__(self):
        """Get number of installed modules
        """
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
        print(f"Image tag : {image_tag}")
        context = module.get_context()
        context = ContextManager().build(context, tag = image_tag)

        # save the module metadata
        sql = "INSERT INTO {} (json, context_id) VALUES (?,?);".format(config.module_info_table)

        conn = self.get_database_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (json.dumps(module.metadata), context.id))
        conn.commit()
        conn.close()
        if verbose:
            sys.stdout.write("done\n".format(module))
            sys.stdout.flush()
 
        return cursor.lastrowid
        
    def __getitem__(self, module_id):
        """Get a ModuleInfo object by id
        """
        sql = "SELECT * FROM {} WHERE id={}".format(config.module_info_table, module_id)
        conn = self.get_database_connection()
        cursor = conn.cursor()
        ans=[r for r in cursor.execute(sql)]
        conn.close()
        if len(ans)==0:
            raise ModuleIDNotFound(module_id)
        m=ModuleInfo.from_json(ans[0][1])
        m.set_id(module_id)
        return m

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
        if task.id is None:
            task.id = self.execute_sql(self.get_task_info_insert_query(task))
        else:
            q=self.get_task_info_update_query(task)
            self.execute_sql(q)
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
        self.clean_tasks()
        
        # start the process
        process = Process(target = self.run_module, args = (task,))
        self.tasks[task_id]=process
        self.tasks[task_id].start()

        return task_id

    def get_context_id(self, module_id):
        """Get a  module's context id
        """
        sql = "SELECT context_id FROM {} WHERE id={}".format(config.module_info_table, module_id)
        conn = self.get_database_connection()
        cursor = conn.cursor()
        a = [r for r in cursor.execute(sql)]
        conn.commit()
        conn.close()
        return a[0][0]


    def run_module(self, task, verbose=False):
        """This function is called by the process in charge of executing the module. Code is executed
        in a new process
        """
        if verbose:
            print("Request run for module id={}, args={}".format(module_id, task["arguments"]))
        # retrieve the module object
        module_id = task["module_id"]
        module = self[module_id]
        # the module's execution context
        context_id = self.get_context_id(module_id)
        # get the command line to send to the container
        command = module.get_cli_command("/output", task["arguments"])
        task["cmd"] = command
        # output directory
        output_dir = task["output_dir"]

        # TODO : add error and stdout handeling
        out = None

        task["start"] = time.time()
        self.save_task(task)
        try:
            out = ContextManager().run(context_id, command, output_dir)

        except Exception as e:
            task["status"]=TaskStatus.ERROR
            task["error"] = str(e).replace("\'", "\"")
            self.save_task(task)
            #print("OUT ", out)
            raise Exception("Module run error {}".format(e))

        # terminate the task at this point
        task["stop"]=time.time()
        task["status"]= TaskStatus.DONE
        self.save_task(task)
        return 

    def has_task(self, task_id):
        """Check if a task exists by id
        """
        tid = int(task_id)
        #print("has task : {}, {}".format(task_id, self.list_tasks()))
        r=tid in [t.id for t in self.list_tasks()]
        #print(r)
        #print([t.id for t in self.list_tasks()])
        return r
    def list_tasks(self):
        """Return list of tasks
        """
        return [t for _,t in self.iter_tasks()]
    def get_task(self, task_id):
        """Get task information
        """
        sql = "SELECT json FROM {} WHERE id={}".format(config.task_info_table, task_id)
        conn = self.get_database_connection()
        cursor = conn.cursor()
        ans=[r for r in cursor.execute(sql)]
        conn.close()
        return TaskInfo.from_json(ans[0][0])

    def kill_task(self, task_id):
        """Kill a task
        """
        task = self.tasks[task_id]
        task.kill()
        del self.tasks[task_id]
        task_output_path = os.path.join(task_outputs, "task_{}".format(task_id))
        self.forcefully_remove_directory(task_output_path)
    def remove_task(self, task_id):
        """Remove a task directory, the task should be done
        """
        self.forcefully_remove_directory(self.get_task_dir(task_id))
    def context_exists(self, context_id):
        """Check that context exists
        """
        return ContextManager().context_exists(context_id)


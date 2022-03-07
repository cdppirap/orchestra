import os
import json
import sqlite3
import pickle as pkl
from multiprocessing import Process
import subprocess

from orchestra.module.info import ModuleInfo
from orchestra.errors import ModuleIDNotFound
from orchestra.environment import ModuleEnvironment

from orchestra.context.manager import ContextManager

import orchestra.configuration as config

class ModuleManager:
    """Class for managing a collection of Module objects, start and stop tasks and more.
    """
    def __init__(self):
        self.init_database()

        self.task_counter = 0
        self.tasks={}

    def init_database(self):
        """Inialize the database, create the module info table
        """
        conn = self.get_database_connection()
        # create tables if they do not exist
        sql = "CREATE TABLE IF NOT EXISTS {} (id integer PRIMARY KEY, json TEXT NOT NULL, context_id TEXT NOT NULL);".format(config.module_info_table)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.close()

    def clear(self):
        """Clear the list of modules and all associated tasks
        """
        sql = "DELETE FROM {}".format(config.module_info_table)
        conn = sqlite3.connect(config.module_database)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()
        
        # clear tasks
        self.clear_tasks()

    def clear_tasks(self):
        """Clear list of tasks
        """
        self.tasks = {}
        self.task_counter = 0
    def iter_modules(self):
        sql = "SELECT * FROM {} ORDER BY id".format(config.module_info_table)
        conn = sqlite3.connect(config.module_database)
        cursor = conn.cursor()
        for row in cursor.execute(sql):
            yield int(row[0]),ModuleInfo.from_json(row[1])
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
        return sqlite3.connect(config.module_database)

    def register_module(self, module, verbose=True):
        """Register a module, returns the module id
        """
        # create the context
        context = module.get_context()
        context = ContextManager().build(context)

        # save the module metadata
        sql = "INSERT INTO {} (json, context_id) VALUES (\'{}\', \'{}\');".format(config.module_info_table, json.dumps(module.metadata), context.id)
        conn = self.get_database_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()

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
    def get_task_dir(self, task_id):
        """Get path of a task directory
        """
        return os.path.join(config.task_directory, "task_{}".format(task_id))
    def start_task(self, module_id, **kwargs):
        """Start a task for a module with the given arguments. All results of the execution are saved
        in a task directory. The id of the task is returned.
        """
        if not module_id in self:
            raise ModuleIDNotFound(module_id)
        task_id = self.task_counter
        self.task_counter += 1
        output_dir = self.get_task_dir(task_id)
        if os.path.exists(output_dir):
            self.forcefully_remove_directory(output_dir)
        os.mkdir(output_dir)
        os.system("chmod a+s {}".format(output_dir))

        process = Process(target = self.run_module, args = (module_id,output_dir,kwargs,))
        self.tasks[task_id]=process
        self.tasks[task_id].start()
        return task_id
    def get_context_id(self, module_id):
        sql = "SELECT context_id FROM {} WHERE id={}".format(config.module_info_table, module_id)
        conn = self.get_database_connection()
        cursor = conn.cursor()
        a = [r for r in cursor.execute(sql)]
        conn.commit()
        conn.close()
        return a[0][0]


    def run_module(self, module_id, output_dir, run_args, verbose=False):
        """This function is called by the process in charge of executing the module. Code is executed
        in a new process
        """
        if verbose:
            print("Request run for module id={}, args={}".format(module_id, run_args))
        module = self[module_id]
        args = module.get_argument_list()
        context_id = self.get_context_id(module_id)
        # activate the environment and execute module
        param_str = " ".join([run_args[k] for k in args])
        error_log = os.path.join("/output", "error.log")
        command = "python -m {} /output {} 2> {}".format(module.get_executable(), 
                #os.path.abspath(output_dir),
                param_str, 
                error_log)
        # TODO : add error handeling
        out = None
        try:
            output_dir = os.path.abspath(output_dir)
            out = ContextManager().run(context_id, command, output_dir)
        except Exception as e:
            raise Exception("Module run error {}".format(e))
        return 
    def has_task(self, task_id):
        """Check if a task exists by id
        """
        tid = int(task_id)
        return tid in self.tasks
    def list_tasks(self):
        """Return list of tasks
        """
        return [t for t in self.tasks]
    def get_task(self, task_id):
        """Get task information
        """
        if not isinstance(task_id, int):
            task_id = int(task_id)
        return self.tasks[task_id]
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


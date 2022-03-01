import os
import pickle as pkl
from multiprocessing import Process
import subprocess

from orchestra.module.info import ModuleInfo
from orchestra.errors import ModuleIDNotFound
from orchestra.environment import create_module_environment

import orchestra.configuration as config

class ModuleManager:
    """Class for managing a collection of Module objects, start and stop tasks and more.
    """
    def __init__(self):
        self.modules={}
        self.task_counter = 0
        self.tasks={}
        self.load()
    def clear(self):
        """Clear the list of modules and all associated tasks
        """
        self.modules = {}
        self.save()
        self.tasks = {}
        self.task_counter = 0
    def load(self, modules_file=config.module_file_path):
        """Load module information from the module file
        """
        if not os.path.exists(modules_file):
            self.modules = {}
        else:
            with open(modules_file, "rb") as f:
                self.modules = pkl.load(f)
    def __contains__(self, module):
        """Check if a module is installed, the input can be either the modules id or a ModuleInfo object
        """
        if isinstance(module, ModuleInfo):
            return module.id in self.modules
        return module in self.modules
    def __len__(self):
        """Get number of installed modules
        """
        return len(self.modules)
    def save(self):
        """Save the current module list to the module file
        """
        with open(config.module_file_path, "wb") as f:
            pkl.dump(self.modules, f)
    def get_next_module_id(self):
        """Get the id value for the next module
        """
        i = len(self.modules)
        while i in self.modules:
            i+=1
        return i
    def register_module(self, module, verbose=True):
        """Register a module, returns the module id
        """
        # create the environment for this module
        module.set_id(self.get_next_module_id())
        module.env_id = create_module_environment(module, verbose=verbose)
        self.modules[module.id] = module
        self.save()
        return module.id
    def __getitem__(self, module_id):
        """Get a ModuleInfo object by id
        """
        if not module_id in self.modules:
            raise ModuleIDNotFound(module_id)
            #raise Exception("Could not find module id={}".format(module_id))
        return self.modules[module_id]
    def remove_module(self, module):
        """Remove a module
        """
        if isinstance(module, ModuleInfo):
            module = self.modules[module.id]
        else:
            module = self.modules[module]
        # remove the virtual environment
        self.forcefully_remove_directory(module.env_id)
        # remove the module from the list
        del self.modules[module.id]
        self.save()
    def forcefully_remove_directory(self, path):
        cmd = "rm -rf {}".format(path)
        #cmd = "rm -rf {} &> /dev/null".format(path)
        os.system(cmd)
    def get_task_dir(self, task_id):
        """Get the path of a task directory
        """
        return os.path.join(config.task_directory, "task_{}".format(task_id))
    def start_task(self, module_id, **kwargs):
        """Start a task for a module with the given arguments. All results of the execution are saved
        in a task directory. The id of the task is returned.
        """
        if not module_id in self.modules:
            raise ModuleIDNotFound(module_id)
        task_id = self.task_counter
        self.task_counter += 1
        output_dir = self.get_task_dir(task_id)
        if os.path.exists(output_dir):
            self.forcefully_remove_directory(output_dir)
        os.mkdir(output_dir)

        process = Process(target = self.run_module, args = (module_id,output_dir,kwargs,))
        self.tasks[task_id]=process
        self.tasks[task_id].start()
        return task_id

    def run_module(self, module_id, output_dir, run_args, verbose=False):
        """This function is called by the process in charge of executing the module. Code is executed
        in a new process
        """
        if verbose:
            print("Request run for module id={}, args={}".format(module_id, run_args))
        module = self[module_id]
        # activate the environment and execute module
        #param_str = " ".join([k for k in list(run_args.values()) if k is not None])
        param_str = " ".join([run_args["parameter"], run_args["start"], run_args["stop"]])
        error_log = os.path.join(output_dir, "error.log")
        cmd = "cd {} ; . bin/activate && python -m {} {} {} 2> {}  && deactivate".format(
                module.environment_path(),
                module.get_executable(),\
                os.path.abspath(output_dir), 
                param_str,
                os.path.abspath(error_log))
        # TODO : add error handeling
        out = None
        try:
            out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        except Exception as e:
            #raise ModuleRunError(e)
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


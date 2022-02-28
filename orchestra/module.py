"""Module management : keeps track of the modules that are installed. 

First implementation : store module information in pickle file. 

Next implementation : store module information in sqlite database (better concurrent access support).

Module information : 
    - module_name : unique identification of a model
    - environement : unique identification of the virtual environement in which it is installed
    - requirements : python requirements for the module
    - files : list of files required by the module
"""
import pickle as pkl
import json
import os
import subprocess
from multiprocessing import Process

from orchestra.errors import *
from orchestra.configuration import *

from orchestra.environement import create_module_environement

class ModuleInfo:
    def __init__(self, path):
        self.path = path
        self.metadata = {}
        self.env_id = None

        # if the module name corresponds with a folder
        if os.path.isdir(path):
            # load from directory
            metadata_path = os.path.join(path, "metadata.json")
            if not os.path.exists(metadata_path):
                raise Exception("Could not find metadata file {}".format(metadata_path))
        elif path.startswith("https://"):
            # clone the repository from github
            module_name = os.path.basename(path).replace(".git","")
            os.system("git clone -c http.sslVerify=0 {}".format(path))
            metadata_path = os.path.join(module_name, "metadata.json")
            self.path = module_name
        else:
            raise Exception("Could not load model name={}".format(name))
        with open(metadata_path,"r") as f:
            self.metadata = json.load(f)
    def is_valid(self):
        mandatory_fields = ["name", "description", "args", "hyperparameters", "output", "defaults", "install"]
        return all([k in self.metadata for k in mandatory_fields])
    def __str__(self):
        if "id" in self.metadata:
            return "Module (id={}, name={}, executable={})".format(self.metadata["id"], self.metadata["name"], self.metadata["install"]["executable"])
        return "Module (name={})".format( self.metadata["name"])

    def get_data(self):
        return self.metadata
    def activation_path(self):
        return os.path.join(self.env_id, "bin/activate")
    def environement_path(self):
        return self.env_id
    def set_id(self, id):
        self.id = id
        self.metadata["id"]=id
    def get_executable(self):
        return self.metadata["install"]["executable"]

class ModuleManager:
    def __init__(self):
        self.modules={}
        self.task_counter = 0
        self.tasks={}
        self.load(module_configuration)
    def clear(self):
        self.modules = {}
        self.save()
        self.tasks = {}
        self.task_counter = 0
        
    def load(self, modules_file=module_configuration):
        if not os.path.exists(modules_file):
            self.modules = {}
        else:
            with open(modules_file, "rb") as f:
                self.modules = pkl.load(f)

    def __contains__(self, module):
        if isinstance(module, ModuleInfo):
            return module.id in self.modules
        return module in self.modules

    def __len__(self):
        return len(self.modules)

    def save(self):
        with open(module_configuration, "wb") as f:
            pkl.dump(self.modules, f)
    
    def get_next_module_id(self):
        i = len(self.modules)
        while i in self.modules:
            i+=1
        return i
    def register_module(self, module, verbose=True):
        # create the environement for this module
        module.set_id(self.get_next_module_id())
        module.env_id = create_module_environement(module, verbose=verbose)
        self.modules[module.id] = module
        self.save()
        return module.id

    def __getitem__(self, module_id):
        if not module_id in self.modules:
            raise ModuleIDNotFound(module_id)
            #raise Exception("Could not find module id={}".format(module_id))
        return self.modules[module_id]

    def remove_module(self, module):
        if isinstance(module, ModuleInfo):
            module = self.modules[module.id]
        else:
            module = self.modules[module]
        # remove the virtual environement
        cmd = "rm -rf {}".format(module.env_id)
        os.system(cmd)
        # remove the module from the list
        del self.modules[module.id]
        self.save()
    
    def get_task_dir(self, task_id):
        return os.path.join(task_directory, "task_{}".format(task_id))
    def start_task(self, module_id, **kwargs):
        if not module_id in self.modules:
            raise ModuleIDNotFound(module_id)
            #raise Exception("Module id={} not found".format(module_id))
        #print("ModuleManager is starting a new task for module {}".format(module_id))
        task_id = self.task_counter
        self.task_counter += 1
        output_dir = self.get_task_dir(task_id)
        if os.path.exists(output_dir):
            os.system("rm -rf {}".format(output_dir))
        os.mkdir(output_dir)

        process = Process(target = self.run_module, args = (module_id,output_dir,kwargs,))
        self.tasks[task_id]=process
        self.tasks[task_id].start()
        return task_id

    def run_module(self, module_id, output_dir, run_args, verbose=False):
        if verbose:
            print("Request run for module id={}, args={}".format(module_id, run_args))
        module = self[module_id]
        # activate the environement and execute module
        #param_str = " ".join([k for k in list(run_args.values()) if k is not None])
        param_str = " ".join([run_args["parameter"], run_args["start"], run_args["stop"]])
        error_log = os.path.join(output_dir, "error.log")
        cmd = "cd {} ; . bin/activate && python -m {} {} {} 2> {}  && deactivate".format(
                module.environement_path(),
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
        tid = int(task_id)
        return tid in self.tasks
    def list_tasks(self):
        return [t for t in self.tasks]
    def get_task(self, task_id):
        if not isinstance(task_id, int):
            task_id = int(task_id)
        return self.tasks[task_id]
    def kill_task(self, task_id):
        task = self.tasks[task_id]
        task.kill()
        del self.tasks[task_id]
        task_output_path = os.path.join(task_outputs, "task_{}".format(task_id))
        os.system("rm -rf {}".format(task_output_path))


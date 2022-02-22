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
from multiprocessing import Process

from orchestra.configuration import module_configuration
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

        self.metadata = json.load(open(metadata_path, "r"))
    def is_valid(self):
        mandatory_fields = ["name", "description", "args", "hyperparameters", "output", "defaults", "install"]
        return all([k in self.metadata for k in mandatory_fields])
    def __str__(self):
        if "id" in self.metadata:
            return "Module (id={}, name={})".format(self.metadata["id"], self.metadata["name"])
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
            self.modules = pkl.load(open(modules_file, "rb"))

    def __contains__(self, module):
        if isinstance(module, ModuleInfo):
            return module.name in self.modules
        return module in self.modules

    def __len__(self):
        return len(self.modules)

    def save(self):
        pkl.dump(self.modules, open(module_configuration, "wb"))
    
    def get_next_module_id(self):
        i = len(self.modules)
        while i in self.modules:
            i+=1
        return i
    def register_module(self, module):
        # create the environement for this module
        module.set_id(self.get_next_module_id())
        module.env_id = create_module_environement(module)
        self.modules[module.id] = module
        self.save()

    def __getitem__(self, module_id):
        return self.modules[module_id]

    def remove_module(self, module):
        if isinstance(module, ModuleInfo):
            module = self.modules[module.name]
        else:
            module = self.modules[module]
        # remove the virtual environement
        os.system("rm -r {}".format(module.env_id))
        # remove the module from the list
        del self.modules[module.name]
        self.save()

    def start_task(self, module_id, **kwargs):
        if not module_id in self.modules:
            raise Exception("Module not found")
        print("ModuleManager is starting a new task for module {}".format(module_id))
        task_id = self.task_counter
        self.task_counter += 1
        output_dir = "task_outputs/task_{}".format(task_id)
        if os.path.exists(output_dir):
            os.system("rm -r {}".format(output_dir))
        os.mkdir(output_dir)

        process = Process(target = self.run_module, args = (module_id,output_dir,kwargs,))
        self.tasks[task_id]=process
        self.tasks[task_id].start()
        return task_id

    def run_module(self, module_id, output_dir, run_args):
        print(run_args)
        module = self[module_id]
        # activate the environement and execute module
        param_str = " ".join([k for k in list(run_args.values()) if k is not None])
        print("param str ", param_str)
        cmd = "cd {} ; . bin/activate ; python -m {} {} {}; deactivate".format(module.environement_path(),module.metadata["name"],\
                os.path.abspath(output_dir), param_str)
        os.system(cmd)
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
        os.system("rm -r task_outputs/task_{}".format(task_id))




if __name__=="__main__":
    print("Module manager tests")
    module_manager = ModuleManager()

    # create a new module
    m = ModuleInfo(name="module1", requirements=["numpy"])
    print(m, type(m), hasattr(m, "get_data"))

    # check if module exists
    if m in module_manager:
        print("Removing module")
        module_manager.remove_module(m)

    # register the new module
    module_manager.register_module(m)

    print("Number of registered modules : {}".format(len(module_manager)))

    for k in module_manager.modules:
        print(module_manager.modules[k])
        print(module_manager.modules[k].get_data())

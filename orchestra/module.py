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
import os
from multiprocessing import Process

from orchestra.configuration import module_configuration
from orchestra.environement import create_module_environement

class ModuleInfo:
    def __init__(self, name, requirements=None, files=[]):
        self.name = name
        self.requirements = requirements
        self.files = files
        self.env_id = None
        self.description="Module"
    def is_valid(self):
        if not self.requirements is None:
            if not os.path.exists(self.requirements):
                return False
        if len(self.files):
            return all([os.path.exists(f) for f in self.files])
        return True
    def __str__(self):
        return "Module ({}, {}, {}, {})".format(self.name, self.requirements, self.files, self.env_id)
    def get_data(self):
        return {"name":self.name,\
                "requirements":self.requirements,\
                "files":self.files,\
                "environement":self.env_id}
    def activation_path(self):
        return os.path.join(self.env_id, "bin/activate")
    def path(self):
        return self.env_id

class ModuleManager:
    def __init__(self):
        self.modules={}
        self.task_counter = 0
        self.tasks={}
        self.load(module_configuration)
        
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
    def register_module(self, module):
        # create the environement for this module
        module.env_id = create_module_environement(module.name, \
                module.requirements,\
                module.files)
        self.modules[module.name] = module
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
        cmd = "cd {} ; . bin/activate ; python -m {} {} {}; deactivate".format(module.path(),module.name,\
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

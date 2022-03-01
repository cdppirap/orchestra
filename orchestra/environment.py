"""Creating environments

Need a list of environments.
"""
import sys
import os
import pickle as pkl
import subprocess

import orchestra.configuration as config

def run_procedure(title, func, *args):
    sys.stdout.write(title+"...")
    sys.stdout.flush()
    ans = func(*args)
    sys.stdout.write("done\n")
    sys.stdout.flush()
    return ans

class ModuleEnvironment:
    def __init__(self, path):
        self.path = path
    def activation_path(self):
        return os.path.join(self.path, "bin/activate")
    def delete(self):
        os.system("rm -rf {} > /dev/null".format(self.path))
    @staticmethod
    def create(module, verbose=True):
        if verbose:
            print("Create module environment for {}".format(module))
        env_dir = os.path.join(config.environment_directory, str(module.id))
        # create the clean virtual environment
        os.system("python3 -m venv {}".format(env_dir))
        # move files into virtual environment
        if verbose:
            run_procedure("Move files", ModuleEnvironment.move_files, module)
        else:
            ModuleEnvironment.move_files(module)
        # install requirements
        if os.path.exists("{}/requirements.txt".format(env_dir)):
            os.system("cat {}/requirements.txt".format(env_dir))
            if verbose:
                run_procedure("Installing requirements", ModuleEnvironment.install_requirements, module)
            else:
                ModuleEnvironment.install_requirements(module)
        return ModuleEnvironment(env_dir)
    @staticmethod
    def save_requirements(requirements, filename):
        if isinstance(requirements, list):
            with open(filename, "w") as f:
                f.write("\n".join(requirements))
        if isinstance(requirements, str):
            if os.path.exists(requirements):
                os.system("cp {} {}".format(requirements, filename))
    @staticmethod
    def move_files(module):
        env_dir = os.path.join(config.environment_directory, str(module.id))
        for f in module.metadata["install"]["files"]:
            filename = os.path.join(module.path, f)
            target_filename = os.path.join(env_dir, os.path.basename(f))
            os.system("cp -r {} {}".format(filename, target_filename))
        # save the requirements file
        if "requirements" in module.metadata["install"] or "requirements.txt" in list(os.listdir(module.path)):
            requirements_file = os.path.join(module.path, "requirements.txt")
            ModuleEnvironment.save_requirements(requirements_file, "{}/requirements.txt".format(env_dir))
     
    @staticmethod
    def install_requirements(module):
        env_dir = os.path.join(config.environment_directory, str(module.id))
        cmd = ". {}/bin/activate ; pip install --upgrade pip ; pip install -r {}/requirements.txt ; deactivate".format(env_dir,env_dir)
        try:
            new_stdout=open("temp_stdout.log","w")
            new_stderr=open("temp_stderr.log","w")
            output = subprocess.check_output([cmd], shell=True, stderr=new_stderr)
            new_stdout.close()
            new_stderr.close()

            f = open("temp_stderr.log","r")
            d=f.read()
            f.close()
            if len(d):
                raise Exception("Install requirements error")
            #output = subprocess.check_output([cmd], shell=True, stderr=subprocess.DEVNULL)
        except Exception as e:
            raise Exception("Failed to install requirements for module {}\n{}".format(module,e))
        return env_dir
    
    @staticmethod
    def run_module(name, cmd):
        os.system("cd {} ;\
                   . bin/activate ;\
                   {} ;\
                   deactivate".format(name, cmd))



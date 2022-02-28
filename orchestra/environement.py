"""Creating environements

Need a list of environements.
"""
import sys
import os
import pickle as pkl
import subprocess

from orchestra.configuration import environement_directory

def save_requirements(requirements, filename):
    if isinstance(requirements, list):
        with open(filename, "w") as f:
            f.write("\n".join(requirements))
    if isinstance(requirements, str):
        if os.path.exists(requirements):
            os.system("cp {} {}".format(requirements, filename))

def create_module_environement(module, verbose=True):
    if verbose:
        print("Create module environement for {}".format(module))
    env_dir = os.path.join(environement_directory, str(module.id))
    # create the clean virtual environement
    os.system("python3 -m venv {}".format(env_dir))
    # move files into virtual environement
    if verbose:
        run_procedure("Move files", move_files, module)
    else:
        move_files(module)
    # install requirements
    if os.path.exists("{}/requirements.txt".format(env_dir)):
        if verbose:
            run_procedure("Installing requirements", install_requirements, module)
        else:
            install_requirements(module)
    return env_dir

def run_procedure(title, func, *args):
    sys.stdout.write(title+"...")
    sys.stdout.flush()
    ans = func(*args)
    sys.stdout.write("done\n")
    sys.stdout.flush()
    return ans

def move_files(module):
    env_dir = os.path.join(environement_directory, str(module.id))
    for f in module.metadata["install"]["files"]:
        filename = os.path.join(module.path, f)
        target_filename = os.path.join(env_dir, os.path.basename(f))
        os.system("cp -r {} {}".format(filename, target_filename))
    # save the requirements file
    if "requirements" in module.metadata["install"] or "requirements.txt" in list(os.listdir(module.path)):
        requirements_file = os.path.join(module.path, "requirements.txt")
        save_requirements(requirements_file, "{}/requirements.txt".format(env_dir))
 

def install_requirements(module):
    env_dir = os.path.join(environement_directory, str(module.id))
    cmd = ". {}/bin/activate ; pip install --upgrade pip ; pip install -r {}/requirements.txt ; deactivate".format(env_dir,env_dir)
    try:
        output = subprocess.check_output([cmd], shell=True, stderr=subprocess.DEVNULL)
    except Exception as e:
        raise Exception("Failed to install requirements for module {}".format(module))
    #os.system(". {}/bin/activate ; pip install --upgrade pip ; pip install -r {}/requirements.txt ; deactivate".format(env_dir,env_dir))
    return env_dir



def run_module(name, cmd):
    os.system("cd {} ;\
               . bin/activate ;\
               {} ;\
               deactivate".format(name, cmd))



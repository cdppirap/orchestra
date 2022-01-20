"""Creating environements

Need a list of environements.
"""
import os
import pickle as pkl

from orchestra.configuration import environement_directory

def save_requirements(requirements, filename):
    if isinstance(requirements, list):
        with open(filename, "w") as f:
            f.write("\n".join(requirements))
    if isinstance(requirements, str):
        if os.path.exists(requirements):
            os.system("cp {} {}".format(requirements, filename))

def create_module_environement(name, requirements=None, files=[]):
    print("Create module ", requirements)
    env_dir = os.path.join(environement_directory, name)
    # create the clean virtual environement
    os.system("python3 -m venv {}".format(env_dir))
    # move files into virtual environement
    for f in files:
        target_filename = os.path.join(env_dir, os.path.basename(f))
        os.system("cp -r {} {}".format(f, target_filename))
    # save the requirements file
    save_requirements(requirements, "{}/requirements.txt".format(env_dir))
    # install requirements
    if os.path.exists("{}/requirements.txt".format(env_dir)):
        print("Installing requirements")
        os.system(". {}/bin/activate ; pip install -r {}/requirements.txt ; deactivate".format(env_dir,env_dir))
    return env_dir


def run_module(name, cmd):
    os.system("cd {} ;\
               . bin/activate ;\
               {} ;\
               deactivate".format(name, cmd))

if __name__=="__main__":
    #remove_module("hahah")
    #exit()
    try:
        register_module("speasy1", "speasy1", files=["test_models/spz.py"], requirements=["speasy"])
    except:
        remove_module("speasy1")
        register_module("speasy1", "speasy1", files=["test_models/spz.py"], requirements=["speasy"])



    print("Registered modules : ")
    modules = load_modules()
    for m in modules:
        print(m)

    run_module("speasy1", "python spz.py amda/imf 2015-01-01 2015-01-02")


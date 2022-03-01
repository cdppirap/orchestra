import argparse
import os

import orchestra.configuration as config
from orchestra.module.info import ModuleInfo
from orchestra.module.manager import ModuleManager

def is_github_repository_address(url):
    return url.startswith("https://") and url.endswith(".git")

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-modules", action="store_true", help="List modules")
    parser.add_argument("--register", type=str, help="Register module")
    parser.add_argument("--requirements", type=str, help="Module requirements")
    parser.add_argument("--files", nargs="+", default=[], help="Module files")
    parser.add_argument("--remove", nargs="+", default=[], help="Remove modules")
    parser.add_argument("--clear", action="store_true", help="Remove all modules and tasks")

    args = parser.parse_args()

    mod_manager = ModuleManager()
    # clear all modules and tasks
    if args.clear:
        os.system("rm -rf {}/*".format(config.environement_directory))
        os.system("rm -rf {}/*".format(config.task_directory))
        mod_manager.clear()
    # register a new model
    if args.register is not None:
        if os.path.exists(args.register):
            mod = ModuleInfo(args.register)
            mod_manager.register_module(mod)
        else:
            if is_github_repository_address(args.register):
                # clone the repository
                os.system("git clone -c http.sslVerify=0 {}".format(args.register))
                repository_folder = os.path.basename(args.register).replace(".git", "")
                mod = ModuleInfo(repository_folder)
                mod_manager.register_module(mod)
                # delete files
                os.system("rm -rf {}".format(repository_folder))

    if len(args.remove):
        for mod in args.remove:
            try:
                index = int(mod)
            except:
                raise Exception("Expected integer module id, got '{}' (type={})".format(mod, type(mod)))
            mod_manager.remove_module(int(mod))
    if args.list_modules:
        print("Registered modules : {}".format(len(mod_manager)))
        for m in mod_manager.modules:
            print("{}. {}".format(m,mod_manager.modules[m]))

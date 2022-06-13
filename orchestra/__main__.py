import argparse
import os
import pwd

import orchestra.configuration as config
from orchestra.module.info import ModuleInfo
from orchestra.module.manager import ModuleManager

def is_github_repository_address(url):
    return url.startswith("https://") and url.endswith(".git")

def get_username():
    return pwd.getpwuid( os.getuid() )[ 0 ]

if __name__=="__main__":
    if get_username() == "root":
        print("You should not run orchestra as root. Exiting...")
        exit()
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-modules", action="store_true", help="List modules")
    parser.add_argument("-R","--register", nargs="+", type=str, help="Register module")
    parser.add_argument("--requirements", type=str, help="Module requirements")
    parser.add_argument("--files", nargs="+", default=[], help="Module files")
    parser.add_argument("--remove", nargs="+", default=[], help="Remove modules")
    parser.add_argument("--clear", action="store_true", help="Remove all modules and tasks")

    args = parser.parse_args()
    
    # initialize the ModuleManager instance
    mod_manager = ModuleManager()
    # clear all modules and tasks
    if args.clear:
        mod_manager.clear()

    # register a new model
    if args.register is not None:
        #print("Register target : {}".format(args.register))
        for target in args.register:
            if os.path.exists(target):
                # metadata path 
                metadata_path = os.path.join(target, "metadata.json")
                mod = ModuleInfo(metadata_path)
                mod_manager.register_module(mod)
            else:
                if is_github_repository_address(target):
                    # clone the repository
                    os.system("git clone -c http.sslVerify=0 {}".format(target))
                    repository_folder = os.path.basename(target).replace(".git", "")
                    metadata_path = os.path.join(repository_folder, "metadata.json")
                    mod = ModuleInfo(metadata_path)
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
        for mid, module in mod_manager.iter_modules():
            print("{}. {}".format(mid,module))

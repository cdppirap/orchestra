import argparse
import os

from orchestra.module import ModuleInfo, ModuleManager
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
    if args.clear:
        os.system("rm -r module_environements/*")
        os.system("rm -r task_outputs/*")
        mod_manager.clear()
    # register a new model
    if args.register is not None:
        ## check if the path corresponds to a folder
        mod = ModuleInfo(args.register)
        # check that module is well defined
        mod_manager.register_module(mod)

    if len(args.remove):
        for mod in args.remove:
            mod_manager.remove_module(mod)
    if args.list_modules:
        print("Registered modules : {}".format(len(mod_manager)))
        for m in mod_manager.modules:
            print(mod_manager.modules[m])

import argparse

from orchestra.module import ModuleInfo, ModuleManager
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-modules", action="store_true", help="List modules")
    parser.add_argument("--register", type=str, help="Register module")
    parser.add_argument("--requirements", type=str, help="Module requirements")
    parser.add_argument("--files", nargs="+", default=[], help="Module files")
    parser.add_argument("--remove", nargs="+", default=[], help="Remove modules")

    args = parser.parse_args()

    mod_manager = ModuleManager()
    # register a new model
    if args.register is not None:
        mod = ModuleInfo(args.register, args.requirements, args.files)
        # check that module is well defined
        if mod.is_valid():
            mod_manager.register_module(mod)
        else:
            raise Exception("Module {} invalid".format(mod))

    if len(args.remove):
        for mod in args.remove:
            mod_manager.remove_module(mod)
    if args.list_modules:
        print("Registered modules : {}".format(len(mod_manager)))
        for m in mod_manager.modules:
            print(m)

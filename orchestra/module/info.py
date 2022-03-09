import os
import json

from orchestra.context import PythonRequirements, PythonContext

mandatory_fields = ["name", "description", "args", "hyperparameters", "output", "defaults", "install"]
class ModuleInfo:
    def __init__(self, filename=None, metadata=None):
        # initialize metadata
        self.id = id
        self.metadata={}
        self.path = None
        if metadata is not None:
            self.metadata=metadata
        # if a filename is given then load from file
        if filename is not None:
            self.path = os.path.dirname(filename)
            with open(filename , "r") as f:
                self.metadata = json.load(f)
    def argument_string(self, args):
        """String of space separated values
        """
        arg_list = self.get_argument_list()
        ag=[]
        for a in arg_list:
            if isinstance(a, list):
                if not a[0] in args:
                    continue
                if args[a[0]] is None:
                    continue
                ag.append("--{} {}".format(a[0], args[a[0]]))
            else:
                if args[a] is None:
                    continue
                ag.append("--{} {}".format(a, args[a]))

        #arg_list = ["--{} {}".format(a, args[a]) for a in arg_list]
        return " ".join(ag)

        return " ".join([args[ak] for ak in arg_list])
    def get_cli_command(self, output_dir, args):
        """Build the command line sequence that will be fed to the module
        """
        error_path = os.path.join(output_dir, "error.log")
        return "python -m {} {} {}".format(self.get_executable(), 
                output_dir, 
                self.argument_string(args))
 
#        return "python -m {} {} {} 2> {}".format(self.get_executable(), 
#                output_dir, 
#                self.argument_string(args),
#                error_path)
    def is_valid(self):
        """Check that the metadata has all mandatory fields
        """
        return all([k in self.metadata for k in mandatory_fields])
    def __str__(self):
        """String representation of the ModuleInfo object
        """
        return "Module (name={}, executable={})".format(self.metadata["name"], self.metadata["install"]["executable"])

    def get_data(self):
        """Get the metadata
        """
        return self.metadata
    def set_id(self, id):
        """Set id of the ModuleInfo object
        """
        self.id = id
        self.metadata["id"]=id
    def get_executable(self):
        """Get the modules executable
        """
        return self.metadata["install"]["executable"]
    def get_argument_list(self):
        """Get the modules argument list
        """
        arglist = self.metadata["args"] + self.metadata["hyperparameters"]
        if not "start" in arglist:
            arglist.append("start")
        if not "stop" in arglist:
            arglist.append("stop")
        return arglist
        #return self.metadata["args"]+["start","stop"]
    @staticmethod
    def from_json(json_data):
        """Load a ModuleInfo object from JSON data structure
        """
        return ModuleInfo(metadata=json.loads(json_data))
    def get_requirements(self):
        if self.path is None:
            return []
        with open(os.path.join(self.path, self.metadata["install"]["requirements"]),"r") as f:
            req=[r for r in f.read().split("\n") if len(r)]
        return req
    def get_files(self):
        return [os.path.abspath(os.path.join(self.path, f)) for f in self.metadata["install"]["files"]]
    def get_context(self):
        requ = PythonRequirements(self.get_requirements())
        context = PythonContext(requirements=requ, files=self.get_files(), python_version=self.get_python_version())
        return context
    def get_output_filenames(self):
        print(self.metadata)
        return self.metadata["output"]["filename"]
    def get_python_version(self):
        if "python_version" not in self.metadata["install"]:
            return "3.6"
        return self.metadata["install"]["python_version"]


import os
import json
from datetime import datetime

from orchestra.context import PythonRequirements, PythonContext

mandatory_fields = ["name", "description", "args", "hyperparameters", "output", "defaults", "install"]

class ModuleInstallationInfo:
    """Class used for storing the installation information needed to create a new module
    """
    def __init__(self, module_id, filename=None, git=None, metadata=None):
        self.module_id = module_id
        self.filename = filename
        self.git = git
        self.metadata = metadata
    def to_json(self):
        return {"module_id": self.module_id,
                "filename": self.filename,
                "git": self.git,
                "metadata": self.metadata,
                }
    @staticmethod
    def from_json(data):
        return ModuleInstallationInfo(**data)

class ModuleInfo:
    def __init__(self, filename=None, metadata=None):
        # initialize metadata
        self.id = None
        self.metadata={}
        self.path = None
        if metadata is not None:
            self.metadata=metadata
            if "id" in metadata:
                self.set_id(metadata["id"])
        # if a filename is given then load from file
        if filename is not None:
            self.path = os.path.dirname(filename)
            with open(filename , "r") as f:
                self.metadata = json.load(f)
                if "id" in self.metadata:
                    self.set_id(self.metadata["id"])

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
 
    def is_valid(self):
        """Check that the metadata has all mandatory fields
        """
        return all([k in self.metadata for k in mandatory_fields])
    def __str__(self):
        """String representation of the ModuleInfo object
        """
        return "ModuleInfo (name={}, executable={})".format(self.metadata["name"], self.metadata["install"]["executable"])

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
        if isinstance(json_data, str):
            return ModuleInfo(metadata=json.loads(json_data))
        return ModuleInfo(metadata=json_data)
    def get_requirements(self):
        if self.path is None:
            return self.metadata["install"].get("requirements", [])
        req = self.metadata["install"].get("requirements", [])
        if self.metadata["install"].get("requirements_file", None) is not None:
            with open(os.path.join(self.path, self.metadata["install"]["requirements_file"]),"r") as f:
                req += [r for r in f.read().split("\n") if len(r)]
        return list(dict.fromkeys(req))
    def set_requirements(self, requirements=None, requirements_file=None):
        if isinstance(requirements,list):
            self.metadata["install"]["requirements"] = requirements
        if requirements_file:
            self.metadata["install"]["requirements_file"] = requirements_file
    def set_python_version(self, v):
        self.metadata["install"]["python_version"] = v
    def get_files(self):
        if self.path is None:
            return self.metadata["install"]["files"]
        return [os.path.abspath(os.path.join(self.path, f)) for f in self.metadata["install"]["files"]]
    def get_context(self):
        requ = PythonRequirements(self.get_requirements())
        context = PythonContext(requirements=requ, files=self.get_files(), python_version=self.get_python_version(), post_process=self.get_post_process())
        return context
    def get_output_filenames(self):
        print(self.metadata)
        return self.metadata["output"]["filename"]
    def get_python_version(self):
        return self.metadata["install"].get("python_version", "3.6")
        if "python_version" not in self.metadata["install"]:
            return "3.6"
        return self.metadata["install"]["python_version"]
    def get_post_process(self):
        if "post_process" not in self.metadata["install"]:
            return []
        if self.metadata["install"]["post_process"] is None:
            return []
        return self.metadata["install"]["post_process"]
    def output_is_timeseries(self):
        return self.metadata["output"]["type"] == "timeseries"
    def output_is_timetable(self):
        return self.metadata["output"]["type"] == "timetable"
    def output_is_catalog(self):
        return self.metadata["output"]["type"] == "catalog"
    def output_filename(self):
        return self.metadata["output"]["filename"]

    def catalog_classes(self):
        if "classes" in self.metadata["output"]:
            return self.metadata["output"]["classes"]
        return [f"cls_{i}" for i in range(10)]
    def catalog_class_colors(self):
        return [[241,196,15],
                [26, 188, 156],
                [39, 176, 96],
                [41, 128, 185],
                [155, 89, 182],
                [192, 57, 43],
                [211, 84, 0],
                [127, 140, 141],
                [44, 62, 80],
                [0, 0, 255]]
    def catalog_class_description(self):
        class_names = self.catalog_classes()
        class_colors = self.catalog_class_colors()
        n_classes = len(class_names)
        class_desc = [f"{i} : {cn} {cc}" for i, cn, cc in zip(range(n_classes), class_names, class_colors)]
        return " - ".join(class_desc)


        
    def header(self, start_date=None, stop_date=None):
        lines = [f"# Name: {self.metadata['name']}"]
        lines += ["# Description:"]
        lines += ["# Prediction from:;"]
        lines += ["# "+l for l in self.metadata["description"].split("\n")]
        if start_date:
            lines += [f"# ListStartDate: {start_date}"]
        else:
            lines += ["# ListStartDate:"]
        if stop_date:
            lines += [f"# ListStopDate: {stop_date}"]
        else:
            lines += ["# ListStopDate:"]
        lines += ["# Contact: CDPP"]
        lines += ["# Historic: ;"]
        lines += [f"# Creation Date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')};"]
        lines += [f"# Parameter 1: id:param_0; name:classes; size:1; type:string; unit:; description:{self.catalog_class_description()}; ucd:; utype:;"]
        return "\n".join(lines)









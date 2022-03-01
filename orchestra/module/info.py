import os
import json

class ModuleInfo:
    def __init__(self, path):
        self.path = path
        self.metadata = {}
        self.env_id = None

        # if the module name corresponds with a folder
        if os.path.isdir(path):
            # load from directory
            metadata_path = os.path.join(path, "metadata.json")
            if not os.path.exists(metadata_path):
                raise Exception("Could not find metadata file {}".format(metadata_path))
        elif path.startswith("https://"):
            # clone the repository from github
            module_name = os.path.basename(path).replace(".git","")
            os.system("git clone -c http.sslVerify=0 {}".format(path))
            metadata_path = os.path.join(module_name, "metadata.json")
            self.path = module_name
        else:
            raise Exception("Could not load model name={}".format(name))
        with open(metadata_path,"r") as f:
            self.metadata = json.load(f)
    def is_valid(self):
        mandatory_fields = ["name", "description", "args", "hyperparameters", "output", "defaults", "install"]
        return all([k in self.metadata for k in mandatory_fields])
    def __str__(self):
        if "id" in self.metadata:
            return "Module (id={}, name={}, executable={})".format(self.metadata["id"], self.metadata["name"], self.metadata["install"]["executable"])
        return "Module (name={})".format( self.metadata["name"])

    def get_data(self):
        return self.metadata
    def activation_path(self):
        return os.path.join(self.env_id, "bin/activate")
    def environment_path(self):
        return self.env_id
    def set_id(self, id):
        self.id = id
        self.metadata["id"]=id
    def get_executable(self):
        return self.metadata["install"]["executable"]



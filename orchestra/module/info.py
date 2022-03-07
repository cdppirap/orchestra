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
        return self.metadata["args"]+["start","stop"]
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
        context = PythonContext(requirements=requ, files=self.get_files())
        return context


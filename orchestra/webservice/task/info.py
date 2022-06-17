"""Task information, data is stored as JSON data in the database

Task data : 
    - id : primary key
    - module_id : key of the module
    - cmd : command line used
    - arguments : dictionary of the arguments passed to the model
    - start_t : start time
    - stop_t : stop time
    - status : status of the task : running, done, error
    - output_directory : output directory
"""
import time
from enum import Enum
import json

class TaskStatus:
    RUNNING="running"
    DONE="done"
    ERROR="error"

class TaskInfo:
    def __init__(self, module_id, kwargs):
        self.id=None
        self.initial_data(module_id, kwargs)
    def initial_data(self, module_id, kwargs):
        self.data = {"start":time.time(),
                "status":TaskStatus.RUNNING,
                "module_id":module_id,
                "arguments":kwargs,
                }
    def __getitem__(self, k):
        return self.data[k]
    def __setitem__(self, k, v):
        self.data[k]=v
    def is_done(self):
        return self["status"]==TaskStatus.DONE or self["status"]==TaskStatus.ERROR
    def get_module_id(self):
        return self.data["module_id"]

    @staticmethod
    def from_json(json_data):
        t = TaskInfo(-1,{})
        if isinstance(json_data, str):
            t.data = json.loads(json_data)
        else:
            t.data = json_data
        if "id" in t.data:
            t.id = t.data["id"]
        return t


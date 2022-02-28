"""Exceptions raised by orchestra
"""

class ModuleIDNotFound(Exception):
    def __init__(self, module_id):
        self.module_id = module_id
        super().__init__()
    def __str__(self):
        return "Module id={} not found".format(self.module_id)

class ModuleRunError(Exception):
    def __init__(self, error):
        self.error=error
        super().__init__()
    def __str__(self):
        return "Module run error : \n{}".format(error)

"""Exceptions raised by orchestra
"""

class ContextCreationError(Exception):
    """Error during context creation, either installing requirements
    or collecting file resources.
    """
    def __init__(self, module_id):
        self.module_id=module_id
    def __str__(self, module_id):
        return "ContextCreationError: module_id={}".format(self.module_id)

class ModuleIDNotFound(Exception):
    """Requested module id was not found
    """
    def __init__(self, module_id):
        self.module_id = module_id
        super().__init__()
    def __str__(self):
        return "Module id={} not found".format(self.module_id)

class ModuleRunError(Exception):
    """Error during model run
    """
    def __init__(self, error):
        self.error=error
        super().__init__()
    def __str__(self):
        return "Module run error : \n{}".format(error)

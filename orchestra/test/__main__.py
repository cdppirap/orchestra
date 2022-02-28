import unittest
import os

from orchestra.errors import *
from orchestra.configuration import *
from orchestra.module import ModuleInfo, ModuleManager

class TestModuleManager(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = ModuleManager()
    def test_manager(self):
        self.assertIsNotNone(self.manager)
        # check that the module container is a dictionary
        self.assertTrue(isinstance(self.manager.modules, dict))
        # count the modules installed
        n = len(self.manager)
        self.assertTrue(isinstance(n, int))
        self.assertTrue(n>=0)
    def test_register_module_from_folder(self):
        n = len(self.manager)
        # install a module
        module_path = "test_modules/module0"
        module = ModuleInfo(module_path)
        module_id=self.manager.register_module(module, verbose=False)
        new_n = len(self.manager)
        self.assertEqual(new_n, n+1)
        self.assertIsNotNone(module_id)

        # get the module by its id
        mod = self.manager[module_id]
        self.assertIsNotNone(mod)
        self.assertEqual(module_id, mod.id)
        # check that the modules virtual environement exists
        environement_path = mod.environement_path()
        self.assertTrue(os.path.exists(environement_path))
        self.assertTrue(module_id in self.manager)
        self.assertTrue(mod in self.manager)

        # remove the module
        self.manager.remove_module(module_id)
        self.assertFalse(os.path.exists(environement_path))
        self.assertFalse(module_id in self.manager)
        self.assertEqual(len(self.manager), n)
        with self.assertRaises(ModuleIDNotFound):
            m = self.manager[module_id]

    def test_register_invalid_module(self):
        module_path = "module_that_does_not_exist"
        with self.assertRaises(Exception):
            m = ModuleInfo(module_path)
    def test_run_module(self):
        # register module1
        module_path = "test_modules/module0"
        module = ModuleInfo(module_path)
        module_id=self.manager.register_module(module, verbose=False)
        module = self.manager[module_id]

        # run the module
        param = "imf"
        start, stop="2000-01-01T00:00:00", "2000-01-02T00:00:00"
        args = {"parameter":param, "start":start, "stop":stop}
        task_id=self.manager.start_task(module_id, **args, verbose=False)

        # check that the task output exists
        self.assertTrue(os.path.exists(task_id))

        # wait for task end
        self.manager.tasks[task_id].join()

        # remove the module
        self.manager.remove_module(module_id)

class TestModuleInfo(unittest.TestCase):
    def test_load_from_folder(self):
        module_path = "test_modules/module0"
        m = ModuleInfo(module_path)
        self.assertIsNotNone(m)


def start_rest_server():
    from orchestra.configuration import rest_host, rest_port
    from orchestra.rest import app
    import sys
    new_stdout = open("temp.out", "w")
    sys.stdout = new_stdout
    sys.stderr = new_stdout
    #
    app.run(host=rest_host, port=rest_port, debug=False)

    new_stdout.close()
class TestRESTAPI(unittest.TestCase):
    def test_rest_api(self):
        from orchestra.rest import app
        from multiprocessing import Process
        import json
        import urllib
        import time
        import sys
        # start rest in another thread
        #rest_process = Process(target=app.run, kwargs={"debug":False})
        rest_process = Process(target=start_rest_server)
        rest_process.start()

        manager = ModuleManager()

        time.sleep(1)

        # get list of modules
        url = "http://127.0.0.1:5000/modules"
        with urllib.request.urlopen(url, timeout=10) as f:
            self.assertIsNotNone(f)
            content = json.loads(f.read())
            self.assertIsNotNone(content)
            
            # check that all modules are present
            self.assertEqual(len(manager), len(content))

        # get module information: register a module first
        module_path = "test_modules/module0"
        module_info = ModuleInfo(module_path)
        module_id = manager.register_module(module_info, verbose=False)
        
        url = "http://127.0.0.1:5000/module/{}".format(module_id)
        with urllib.request.urlopen(url, timeout=10) as f:
            self.assertIsNotNone(f)
            content = json.loads(f.read())
            self.assertIsNotNone(content)
            fields=["id","name","description", "args", "hyperparameters", "defaults", "output", "install"]
            for field in fields:
                self.assertTrue(module_info.metadata[field] == content[field])

        # run the module
        url = "http://127.0.0.1:5000/module/{}/run?parameter=imf&start=2000-01-01T00:00:00&stop=2000-01-02T00:00:00".format(module_id)
        task_id = None
        with urllib.request.urlopen(url, timeout=10) as f:
            self.assertIsNotNone(f)
            content = json.loads(f.read())
            self.assertIsNotNone(content)
            self.assertTrue(isinstance(content["task"], int))
            task_id = content["task"]
        
        # give some time for the task to end
        time.sleep(1)

        # get the status of the module run
        url = "http://127.0.0.1:5000/task/{}".format(task_id)
        task_data = None
        with urllib.request.urlopen(url, timeout=10) as f:
            self.assertIsNotNone(f)
            content = json.loads(f.read())
            self.assertIsNotNone(content)
            fields = ["status", "output", "error", "id"]
            self.assertTrue(all([k in content for k in fields]))
            self.assertTrue(content["status"]=="done")
            task_data = content

        # get the task output
        url = "http://127.0.0.1:5000/task/{}/output".format(task_id)
        with urllib.request.urlopen(url, timeout=10) as f:
            task_files = task_data["output"]
            content = f.read()
            self.assertIsNotNone(content)
            # get the output file from task folder
            task_folder = manager.get_task_dir(task_id)
            self.assertTrue(os.path.exists(task_folder))
            # check files on local hard drive
            for fi in os.listdir(task_folder):
                if fi in task_files:
                    ff = open(os.path.join(task_folder, fi), "rb")
                    conteont = ff.read()
                    ff.close()
                    self.assertTrue(conteont, content)
            
        # kill process
        rest_process.kill()
        rest_process.join()

        # remove the module
        manager.remove_module(module_id)

if __name__=="__main__":
    unittest.main()

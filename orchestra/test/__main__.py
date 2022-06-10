import unittest
import os
import urllib.request
from multiprocessing import Process
import json
import time
import sys
 

from orchestra.errors import *
from orchestra.configuration import *
from orchestra.module.info import ModuleInfo
from orchestra.module.manager import ModuleManager

class TestModuleManager(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        """Test the ModuleManager implementation
        """
        super().__init__(*args, **kwargs)
        self.manager = ModuleManager()
    def test_manager(self):
        """Test that the manager is well instanciated
        """
        self.assertIsNotNone(self.manager)
        # count the modules installed
        n = len(self.manager)
        self.assertTrue(isinstance(n, int))
        self.assertTrue(n>=0)
    def test_register_module_from_folder(self):
        """Test registering module from a folder
        """
        n = len(self.manager)
        # install a module
        module_path = "test_modules/module0"
        module_metadata_path= os.path.join(module_path, "metadata.json")
        module = ModuleInfo(module_metadata_path)
        module_id=self.manager.register_module(module, verbose=False)
        new_n = len(self.manager)
        self.assertEqual(new_n, n+1)
        self.assertIsNotNone(module_id)

        # get the module by its id
        mod = self.manager[module_id]
        self.assertIsNotNone(mod)
        self.assertEqual(module_id, mod.id)
        # check that the modules context has been created
        context_id = self.manager.get_context_id(module_id)

        self.assertTrue(module_id in self.manager)
        self.assertTrue(self.manager.context_exists(context_id))

        # remove the module
        self.manager.remove_module(module_id)
        self.assertFalse(module_id in self.manager)
        self.assertEqual(len(self.manager), n)
        with self.assertRaises(ModuleIDNotFound):
            m = self.manager[module_id]
    def test_register_invalid_module(self):
        """Test registering an invalid module
        """
        module_path = "module_that_does_not_exist"
        with self.assertRaises(Exception):
            m = ModuleInfo(module_path)
    def test_run_module(self, module_path = "test_modules/module0"):
        """Test running a module
        """
        # register module1
        #module_path = "test_modules/module0"
        module_metadata_path = os.path.join(module_path, "metadata.json")
        module = ModuleInfo(module_metadata_path)
        module_id=self.manager.register_module(module, verbose=False)
        module = self.manager[module_id]

        # run the module
        param = "imf"
        start, stop="2000-01-01T00:00:00", "2000-01-02T00:00:00"
        args = {"parameter":param, "start":start, "stop":stop}
        task_id=self.manager.start_task(module_id, args)
        task_output_path = self.manager.get_task_dir(task_id)

        # check that the task output exists
        self.assertTrue(os.path.exists(task_output_path))

        # wait for task end
        self.manager.tasks[task_id].join()

        # remove the module
        self.manager.remove_module(module_id)
    def test_multiple_module(self):
        module_list = ["module0", "module1", "module2", "module3", "speasy1", 
                "test_breuillard", "test_cat_module", "test_cat_module_1_param",
                "test_cat_subzero_module", "test_module_heavy", "test_ts_module",
                "test_tt_module"]
        module_paths = [os.path.join("test_modules", m) for m in module_list]
        for mod in module_paths: 
            self.test_run_module(mod)

class TestModuleInfo(unittest.TestCase):
    """Test module info implementation
    """
    def test_load_from_folder(self):
        module_path = "test_modules/module0"
        module_metadata_path=os.path.join(module_path, "metadata.json")
        m = ModuleInfo(module_metadata_path)
        self.assertIsNotNone(m)


def start_rest_server():
    """Start the REST server in a separate process
    """
    from orchestra.configuration import rest_host, rest_port
    from orchestra.rest import app
    new_stdout = open("/dev/null", "w")
    sys.stdout = new_stdout
    sys.stderr = new_stdout
    #
    app.run(host=rest_host, port=rest_port, debug=False)

    new_stdout.close()
    #os.system("rm -rf temp.out")

class TestRESTAPI(unittest.TestCase):
    """Test the REST API implementation
    """
    def test_rest_api(self):
        """Test REST API
        """
        from orchestra.rest.urls import get_rest_modules_url,\
                get_rest_module_info_url,\
                get_rest_module_run_url,\
                get_rest_tasks_url,\
                get_rest_task_info_url,\
                get_rest_task_output_url

        # start rest in another thread
        #rest_process = Process(target=app.run, kwargs={"debug":False})
        rest_process = Process(target=start_rest_server)
        rest_process.start()

        manager = ModuleManager()

        time.sleep(1)

        # get list of modules
        url = get_rest_modules_url()
        with urllib.request.urlopen(url, timeout=10) as f:
            self.assertIsNotNone(f)
            content = json.loads(f.read())
            self.assertIsNotNone(content)
            
            # check that all modules are present
            self.assertEqual(len(manager), len(content))

        # get module information: register a module first
        module_path = "test_modules/module0"
        module_metadata_path = os.path.join(module_path, "metadata.json")
        module_info = ModuleInfo(module_metadata_path)
        module_id = manager.register_module(module_info, verbose=False)
        
        url = get_rest_module_info_url(module_id)
        with urllib.request.urlopen(url, timeout=10) as f:
            self.assertIsNotNone(f)
            content = json.loads(f.read())
            self.assertIsNotNone(content)
            fields=["name","description", "args", "hyperparameters", "defaults", "output", "install"]
            self.assertTrue(module_id, content["id"])
            for field in fields:
                self.assertTrue(module_info.metadata[field] == content[field])

        # run the module
        url = get_rest_module_run_url(module_id, **{"parameter":"imf",
                                            "start":"2000-01-01T00:00:00",
                                            "stop":"2000-01-02T00:00:00"})
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
        url = get_rest_task_info_url(task_id)
        task_data = None
        with urllib.request.urlopen(url, timeout=10) as f:
            self.assertIsNotNone(f)
            content = json.loads(f.read())
            self.assertIsNotNone(content)
            fields = ["status", "output_dir", "id"]
            self.assertTrue(all([k in content for k in fields]))
            print(content["status"], " should equals done")
            self.assertTrue(content["status"]=="done")
            task_data = content

        # get the task output
        url = get_rest_task_output_url(task_id)
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
        #rest_process.kill()
        rest_process.terminate()
        rest_process.join()

        # remove the module
        manager.remove_module(module_id)
        manager.remove_task(task_id)

if __name__=="__main__":
    unittest.main()

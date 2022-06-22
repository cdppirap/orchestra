import os
import zipfile
import tempfile
import uuid

from celery import shared_task
# database
from .db import get_db
from .models import Module, Task

# module manager and info
from .module.info import ModuleInfo, ModuleInstallationInfo
from .module.manager import ModuleManager
# tasks
from .task.info import TaskInfo

@shared_task
def sleepy(t):
    import time
    t0 = time.time()
    time.sleep(t)
    return time.time() - t0

@shared_task
def run_module(task_data):
    """Start execution of a module
    """
    # database connection
    db = get_db()
    # get task info
    task = Task.query.get(task_data["task_id"])
    task.celery_id = run_module.request.id
    db.session.commit()
    # create the TaskInfo object
    #task = TaskInfo.from_json(task_data)
    module_manager = ModuleManager()
    module_manager.run_module(task.info())

def find_files(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            yield os.path.join(root, name)


@shared_task
def register_module(module_install_data):
    """Module registration task
    """

    module_install = ModuleInstallationInfo.from_json(module_install_data)
    module_manager = ModuleManager()
    db = get_db()
    if module_install.filename:
        # unzip the file and register the module
        with zipfile.ZipFile(module_install.filename, "r") as zip_ref:
            # create a temporary directory in which to unzip
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_ref.extractall(temp_dir)
                # register modules found in archive (can be more then one)
                first_module = True
                for metadata_path in find_files("metadata.json", temp_dir):
                    #metadata_path = os.path.join(temp_dir, "metadata.json")
                    module_info = ModuleInfo(metadata_path)
                    if first_module:
                        # we can set the id because a Module entry exists
                        module_info.set_id(module_install.module_id)
                    else:
                        # create a new pending entry
                        temp_name = "TempModule_" + uuid.uuid4().hex[:4].upper()
                        new_mod = Module(status="pending", name=temp_name)
                        # save the new Module
                        db.session.add(new_mod)
                        db.session.commit()
                        db.session.refresh(new_mod)
                        module_install.module_id = new_mod.id
                        module_info.set_id(module_install.module_id)



                    module = Module.query.get(module_install.module_id)
                    module.name = module_info.metadata["name"]
                    db.session.commit()

                                    # register the module
                    mdata, context_id = module_manager.register_module(module_info)
                    # update the module object
                    module.load_json(mdata)
                    module.context_id = context_id
                    if context_id is not None:
                        module.status = "installed"
                        db.session.commit()
                    else:
                        module.status = "error"
                    first_module = False


                        
    elif module_install.git:
        with tempfile.TemporaryDirectory() as temp_dir:
            current_dir = os.getcwd()
            os.chdir(temp_dir)
            os.system(f"git clone -c http.sslVerify=0 {module_install.git}")
            repository_folder = os.path.basename(module_install.git).replace(".git", "")
            metadata_path = os.path.join(repository_folder, "metadata.json")
            module_info = ModuleInfo(metadata_path)
            module_info.set_id(module_install.module_id)
            module = Module.query.get(module_info.id)
            module.name = module_info.metadata["name"]
            db.session.commit()

            # register the module
            mdata, context_id = module_manager.register_module(module_info)
            # update the module object
            module.load_json(mdata)
            module.context_id = context_id
            if context_id is not None:
                module.status = "installed"
            else:
                module.status = "error"

            db.session.commit()


            # move back to original directory
            os.chdir(current_dir)

    else:
        print("Module registration: nothing to do.")
        return

    # commit
    db.session.commit()
    # close database session
    db.session.close()




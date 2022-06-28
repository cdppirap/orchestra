import os
import zipfile
import tempfile
import uuid
import json

from celery import shared_task
# database
from .db import get_db
from .models import Module, Task

# module manager and info
from .module.info import ModuleInfo, ModuleInstallationInfo
from .module.manager import ModuleManager
# context manager
from ..context.manager import ContextManager
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
    result = module_manager.run_module(task.info())


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
                    # read the requirements file if exists and populate the module_info.metadata dict
                    module_info.metadata["install"]["requirements"] = module_info.get_requirements()
                    module_info.metadata["install"].pop("requirements_file", None)
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
                    module.install_source = module_install.filename
                    if context_id is not None:
                        module.status = "installed"
                        db.session.commit()
                    else:
                        module.status = "error"
                    first_module = False


                        
    elif module_install.git:
        with tempfile.TemporaryDirectory() as temp_dir:
            current_dir = os.getcwd()
            #os.chdir(temp_dir)
            os.system(f"git clone -c http.sslVerify=0 {module_install.git} {temp_dir}")
            repository_name = os.path.basename(module_install.git).replace(".git", "")
            metadata_path = os.path.join(temp_dir, "metadata.json")
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
            module.install_source = module_install.git
            if context_id is not None:
                module.status = "installed"
            else:
                module.status = "error"

            db.session.commit()


            # move back to original directory
            #os.chdir(current_dir)

    else:
        print("Module registration: nothing to do.")
        return

    # commit
    db.session.commit()
    # close database session
    db.session.close()

@shared_task
def reinstall_module(module_id):
    # database connection
    db = get_db()
    # module manager
    module_manager = ModuleManager()
    # context manager
    cmanager = ContextManager()
    module = Module.query.get(module_id)
    # remove the previously built image
    cmanager.remove(module.context_id)
    module.context_id = None
    module.status = "pending"
    # remove the duplicated requirements before save
    temp_req = json.loads(module.requirements)
    temp_req = list(dict.fromkeys(temp_req))
    module.requirements = json.dumps(temp_req)

    db.session.commit()
    db.session.refresh(module)

    print(f"Reinstalling module : {module}")
    # install from an archive
    if os.path.exists(module.install_source):
        # unzip the archive
        with zipfile.ZipFile(module.install_source, "r") as zip_ref:
            # create a temporary directory in which to unzip
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_ref.extractall(temp_dir)
                for metadata_path in find_files("metadata.json", temp_dir):
                    # check if the name corresponds
                    with open(metadata_path,"r") as f:
                        metadata = json.loads(f.read())
                        if metadata["name"] == module.name:
                            # reinstall this module, load the metadata from the database (not the json file)
                            module_info = module.info()
                            # set the root path correctly, directory containing the metadata file
                            module_info.path = os.path.dirname(metadata_path)

                            # register the module
                            mdata, context_id = module_manager.register_module(module_info)
                            # update the module object
                            module.context_id = context_id
                            module.load_json(mdata)
                            if context_id is not None:
                                module.status = "installed"
                            else:
                                module.status = "error"

                            db.session.commit()
    elif module.install_source.startswith("https://"):
        with tempfile.TemporaryDirectory() as temp_dir:
            current_dir = os.getcwd()
            #os.chdir(temp_dir)
            os.system(f"git clone -c http.sslVerify=0 {module.install_source} {temp_dir}")
            repository_name = os.path.basename(module.install_source).replace(".git", "")
            metadata_path = os.path.join(temp_dir, "metadata.json")
            module_info = ModuleInfo(metadata_path)
            # requirements should be set from the database Module entry
            #module_info.set_python_version(module.python_version)
            #module_info.set_requirements(requirements=json.loads(module.requirements), requirements_file=module.requirements_file)
            module_info = module.info()
            module_info.path=os.path.dirname(metadata_path)

            # register the module
            mdata, context_id = module_manager.register_module(module_info)
            # update the module object
            module.load_json(mdata)
            module.context_id = context_id
            if context_id is not None:
                module.status = "installed"
            else:
                module.status = "error"

            # move back to original directory
            #os.chdir(current_dir)
            db.session.commit()
    else:
        if not os.path.exists(module.install_source):
            module.status = "error"
            module.build_log=f"Unable to reinstall module {module.id}. File {module.install_source} not found."
            db.session.commit()
            raise Exception(f"Unable to reinstall module {module.id}. File {module.install_source} not found.")








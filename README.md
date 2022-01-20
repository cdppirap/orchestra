# Python virtual environement manager

Orchestra is a collection of functions for creating virtual environements. It will be one of the
components of AMDAs Machine Learning Pipeline. 

The main object in this module is a daemon process that allows users to execute python modules in a
protected environement. 

## Endpoints

The list of endpoints : 
    - modules : list of modules
    - module/<module_id> : module information
    - module/<module_id>/run [args] : execute a module
    - tasks : list of tasks
    - task/<task_id> : task information
    - task/<task_id>/output : get task output
    - task/<task_id>/kill : kill task

## Installing modules
This is the procedure that needs to be followed to install a new module.

python -m orchestra --register <module_name> --requirements requirements.txt --files <file_1> ... <file_n>



## REST client

Orchestra exposes a REST API that can be used to request predictions of the models installed.
The required information. 
        model_id
        parameter_id
        start_time
        stop_time

Registration of a new model. Files needed are the script.py and requirements.txt files. The register
command adds the script, associating with it a unique id and some metadata. 
	orchestra --register script.py requirements.txt

List the models installed : 
	orchestra --list
	Model id
        --------
        model_1, script.py, requirements.txt
        ...
        model_n, script_n.py, requirements.txt

## Running the models
Orchestra uses docker containers to execute code. When a module is registered an image is created.



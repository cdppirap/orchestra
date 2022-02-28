# Python virtual environement manager

Orchestra is a collection of tools for managing the backend part of AMDA's machine learning pipeline. Orchestra uses Flask to expose a REST API used by AMDA's internal components to retrieve
information about the modules that are installed, create new prediction or training tasks, and more.

Each machine learning model is implemented as a `python module` that is installed with all its requirements in a dedictated virtual environement. 

## REST API endpoints

List of endpoints exposed by the REST API : 
    - modules : retrieve a list of modules and assiciated metadata
    - module/<int:module_id> : specific module metadata
    - module/<int:module_id>/run [args] : request executing specified model with arguments supplied by user
    - tasks : retrieve list of tasks and associated metadata
    - task/<int:task_id> : specific task metadata (status, errors, output, ...)
    - task/<int:task_id>/output : download task output
    - task/<int:task_id>/kill : kill task

## Installing a new module

Modules are installed by passing the `--register` parameter to `orchestra` with a path pointing to either : 
    - a folder containing a python module
    - a github repository containing a python module
In both cases the root of the target folder must contain a `metadata.json` file. This file contains all metadata describing the model as well as a list of files required to create a virtual environement 
(requirements, files, etc...).

### From folder

The module is located in `/path/to/module/Model`. The `/path/to/module` looks like :
    - metadata.json
    - requirements.txt
    - Model
        - __init__.py
        - ...

The module is installed with : 

python -m orchestra --register /path/to/module

### From GitHub

The module is stored in a GitHub repository, install it with : 

python -m orchestra --register https://github.com/module_repository.git

### List of modules

The user can list the modules that are installed with : 

python -m orchestra --list


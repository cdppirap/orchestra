"""Orchestra REST API

Endpoints : - modules : list of installed modules
            - modules/<module_id> : module information
            - modules/<module_id>/run : run the module
            - modules/<module_id>/train : train the module

"""
import tempfile
import os
import json

from flask import Flask, request, send_from_directory, redirect, Response
from flask_restful import Resource, Api, reqparse
from flask_basicauth import BasicAuth
from werkzeug.exceptions import HTTPException

from orchestra.webservice.module.info import ModuleInfo
from orchestra.webservice.module.manager import ModuleManager

# Database
from flask_sqlalchemy import SQLAlchemy

# REST endpoints
from .resources import *

import orchestra.configuration as config


def init_app(app):
    api = Api(app)

    # REST endpoints
    # module related 
    api.add_resource(ListModules, "/modules")
    api.add_resource(ShowModule, "/modules/<string:module_id>")
    api.add_resource(RunModule, "/modules/<string:module_id>/run")
    
    # task related
    api.add_resource(ListTasks,"/tasks")
    api.add_resource(ShowTask, "/tasks/<int:task_id>")
    api.add_resource(KillTask, "/tasks/<int:task_id>/kill")
    api.add_resource(TaskOutput, "/tasks/<int:task_id>/output")



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

from orchestra.module.info import ModuleInfo
from orchestra.module.manager import ModuleManager

# Database
from flask_sqlalchemy import SQLAlchemy

# REST endpoints
from orchestra.rest.resources import *
# Administration
from orchestra.webservice.admin import *


import orchestra.configuration as config


app = Flask(__name__)
api = Api(app)


# administration
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
# basic authentification
app.config["BASIC_AUTH_USERNAME"] = "admin"
app.config["BASIC_AUTH_PASSWORD"] = "orchestra_admin"
# database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orchestra.sqlite3"

# database connection
db = SQLAlchemy(app)

#class ModuleInformation(db.Model):
#    id = db.Column("module_id", db.Integer, primary_key=True)
#    name = db.Column(db.String(256))
#    metadata = db.Column(db.String(2048))
#
#class TaskInformation(db.Model):
#    id = db.Column("task_id", db.Integer, primary_key=True)
#    module_id = db.Column(db.Integer)
#    metadata = db.Column(db.String(2048))

# initialize the database
db.create_all()


basic_auth = BasicAuth(app)

# Administration view
admin = Admin(app, name="orchestra", template_mode="bootstrap3", 
        index_view=OrchestraAdminIndexView(basic_auth))

# Module creation view


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



import json

from flask_sqlalchemy import SQLAlchemy
#from flask_sqlalchemy.sqlalchemy.orm import relationship
from flask import current_app, g, url_for

#db = SQLAlchemy()
from .db import db, get_db

from .module.info import ModuleInfo
from .task.info import TaskInfo



class Module(db.Model):
    __tablename__="module"
    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=True)
    description = db.Column(db.Text, nullable=True)
    arguments = db.Column(db.Text, nullable=True)
    hyperparameters = db.Column(db.Text, nullable=True)
    default_args = db.Column(db.Text, nullable=True)
    #default_hyperargs = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(48), nullable=True, default="pending")
    context_id = db.Column(db.String(128), nullable=True)
    debug_flag = db.Column(db.Boolean, default=True)

    # context creation
    python_version = db.Column(db.String(4), nullable=False, default="3.8")
    requirements = db.Column(db.Text, nullable=True)
    requirements_file = db.Column(db.String(256), nullable=True)
    files = db.Column(db.Text, nullable=True)
    executable = db.Column(db.String(256), nullable=True)
    pre_process = db.Column(db.Text, nullable=True)
    post_process = db.Column(db.Text, nullable=True)

    build_log = db.Column(db.Text, nullable=True)

    # installation source
    install_source = db.Column(db.String(256), nullable=True)
    
    tasks = db.relationship("Task", backref=db.backref("module", lazy=True))

    def output_is_catalog(self):
        return json.loads(self.output)["type"] == "catalog"

    def output_filename(self):
        return json.loads(self.output)["filename"]

    def __repr__(self):
        return f"Module(id={self.id}, name={self.name})"

    def details_link(self):
        url = url_for("module.details_view", id=self.id)
        return f"<a href='{url}'>{self}</a>"

    def to_json(self):
        return {"id": self.id,
                "name": self.name,
                "description": self.description,
                "args": json.loads(self.arguments),
                "hyperparameters": json.loads(self.hyperparameters),
                "defaults": json.loads(self.default_args),
                "output": json.loads(self.output),
                "install": {
                    "python_version": self.python_version,
                    "requirements": json.loads(self.requirements),
                    "requirements_file": self.requirements_file,
                    "files": json.loads(self.files),
                    "executable": self.executable,
                    "pre_process": json.loads(self.pre_process),
                    "post_process": json.loads(self.post_process),
                    },
                "status": self.status,
                "build_log": self.build_log,
                }
    def load_json(self, data):
        self.name = data["name"]
        self.description = data["description"]
        self.arguments = json.dumps(data["args"])
        self.hyperparameters = json.dumps(data["hyperparameters"])
        self.default_args = json.dumps(data["defaults"])
        #if "hyperparameters" in data["defaults"]:
        #    self.default_hyperargs = json.dumps(data["defaults"]["hyperparameters"])
        #else:
        #    self.default_hyperargs = "[]"
        self.output = json.dumps(data["output"])

        # module install data
        self.python_version = data["install"].get("python_version","3.8")
        temp_requirements = data["install"].get("requirements",[])
        temp_requirements = list(dict.fromkeys(temp_requirements))
        self.requirements = json.dumps(temp_requirements)

        self.requirements_file = data["install"].get("requirements_file", None)
        self.files = json.dumps(data["install"]["files"])
        self.executable = data["install"]["executable"]
        self.pre_process = json.dumps(data["install"].get("pre_process", []))
        self.post_process = json.dumps(data["install"].get("post_process", []))

        # internal data
        if "status" in data:
            self.status = data["status"]
        if "build_log" in data:
            self.build_log= data["build_log"]

    def info(self):
        """Get ModuleInfo object
        """
        return ModuleInfo.from_json(self.to_json())


class Task(db.Model):
    __tablename__="task"
    id= db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Float)
    stop = db.Column(db.Float)
    status = db.Column(db.String(48))
    module_id = db.Column(db.Integer, db.ForeignKey("module.id"))
    arguments = db.Column(db.Text)
    output_dir = db.Column(db.String(1024))
    command = db.Column(db.String(1024))
    celery_id = db.Column(db.String(256))

    #module = db.relationship("Module")

    # execution log
    execution_log = db.Column(db.Text)
    def __repr__(self):
        return f"Task(id={self.id})"


    def details_link(self):
        url = url_for("task.details_view", id=self.id)
        return f"<a href='{url}'>{self}</a>"


    def to_json(self):
        return {"id": self.id,
                "start": self.start,
                "stop": self.stop,
                "status": self.status,
                "module_id": self.module_id,
                "arguments": json.loads(self.arguments),
                "output_dir": self.output_dir,
                "cmd": self.command,
                "celery_id": self.celery_id,
                }
    def load_json(self, data):
        print(data)
        if "id" in data:
            self.id= data["id"]
        self.start = data["start"]
        if "stop" in data:
            self.stop = data["stop"]
        else:
            self.stop = None
        self.status = data["status"]
        self.module_id = data["module_id"]
        self.arguments = json.dumps(data["arguments"])
        if "celery_id" in data:
            self.celery_id = data["celery_id"]
        else:
            self.celery_id = None
        if "output_dir" in data:
            self.output_dir = data["output_dir"]
        else:
            self.output_dir = None
        if "cmd" in data:
            self.command = data["cmd"]
        else:
            self.command = None

        self.execution_log = data.get("execution_log", None)



    def info(self):
        """Get TaskInfo object
        """
        return TaskInfo.from_json(self.to_json())

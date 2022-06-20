import json

from flask_sqlalchemy import SQLAlchemy
#from flask_sqlalchemy.sqlalchemy.orm import relationship
from flask import current_app, g

#db = SQLAlchemy()
from .db import db

from .module.info import ModuleInfo
from .task.info import TaskInfo

class Module(db.Model):
    __tablename__="module"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=True)
    description = db.Column(db.Text, nullable=True)
    arguments = db.Column(db.Text, nullable=True)
    hyperparameters = db.Column(db.Text, nullable=True)
    default_args = db.Column(db.Text, nullable=True)
    #default_hyperargs = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=True)
    install = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(48), nullable=True, default="pending")
    context_id = db.Column(db.String(128), nullable=True)
    debug_flag = db.Column(db.Boolean, default=True)
    
    tasks = db.relationship("Task", backref=db.backref("module", lazy=True))

    def __repr__(self):
        return f"Module(id={self.id}, name={self.name})"

    def to_json(self):
        return {"name": self.name,
                "description": self.description,
                "args": json.loads(self.arguments),
                "hyperparameters": json.loads(self.hyperparameters),
                "defaults": json.loads(self.default_args),
                "output": json.loads(self.output),
                "install": json.loads(self.install),
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
        self.install = json.dumps(data["install"])

    def info(self):
        """Get ModuleInfo object
        """
        return ModuleInfo.from_json(self.to_json())


class Task(db.Model):
    __tablename__="task"
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Float)
    stop = db.Column(db.Float)
    status = db.Column(db.String(48))
    module_id = db.Column(db.Integer, db.ForeignKey("module.id"))
    arguments = db.Column(db.Text)
    output_dir = db.Column(db.String(1024))
    command = db.Column(db.String(1024))
    celery_id = db.Column(db.String(256))

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
            self.id = data["id"]
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



    def info(self):
        """Get TaskInfo object
        """
        return TaskInfo.from_json(self.to_json())

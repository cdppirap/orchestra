from flask_sqlalchemy import SQLAlchemy
from flask import current_app, g

#db = SQLAlchemy()
from .db import db

from .module.info import ModuleInfo
from .task.info import TaskInfo

class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

class Module(db.Model):
    __tablename__="model"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=True)
    json = db.Column(db.Text, nullable=False)
    context_id = db.Column(db.String(128), nullable=False)

    def info(self):
        """Get ModuleInfo object
        """
        return ModuleInfo.from_json(self.json)


class Task(db.Model):
    __tablename__="task"
    id = db.Column(db.Integer, primary_key=True)
    #module_id = db.Column(db.Integer)
    #status = db.Column(db.String(80), nullable=False)
    json = db.Column(db.Text, nullable=False)

    def info(self):
        """Get TaskInfo object
        """
        return TaskInfo.from_json(self.json)

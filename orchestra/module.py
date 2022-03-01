"""Module management : keeps track of the modules that are installed. 

First implementation : store module information in pickle file. 

Next implementation : store module information in sqlite database (better concurrent access support).

Module information : 
    - module_name : unique identification of a model
    - environement : unique identification of the virtual environement in which it is installed
    - requirements : python requirements for the module
    - files : list of files required by the module
"""
import pickle as pkl
import json
import os
import subprocess
from multiprocessing import Process

from orchestra.errors import *
from orchestra.configuration import *

from orchestra.environement import create_module_environement



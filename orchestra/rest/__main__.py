import os
import pwd

from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api, reqparse


from orchestra.rest import *

def get_username():
    return pwd.getpwuid( os.getuid() )[ 0 ]


if __name__=="__main__":
    if get_username() == "root":
        print("You should not run orchestra as root. Exiting...")
        exit()
 
    from orchestra.configuration import rest_host, rest_port
    app.run(host=rest_host, port=rest_port, debug=True)

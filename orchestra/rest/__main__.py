import os
import pwd
import argparse

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

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, help="REST service port", default=rest_port)
    parser.add_argument("--host", type=str, help="REST service host", default=rest_host)
    parser.add_argument("--debug", action="store_true", help="Debug mode")

    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)

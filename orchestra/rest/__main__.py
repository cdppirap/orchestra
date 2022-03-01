from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api, reqparse


app = Flask(__name__)
api = Api(app)

if __name__=="__main__":
    from orchestra.configuration import rest_host, rest_port
    app.run(host=rest_host, port=rest_port, debug=True)


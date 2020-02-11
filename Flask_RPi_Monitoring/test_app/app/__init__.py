from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api, reqparse

# Open flask and all
application = Flask(__name__)
api = Api(application)
parser = reqparse.RequestParser()
auth = HTTPBasicAuth()

# setup folders to save files that are uploaded (need to be downloaded)
UPLOAD_FOLDER = 'app/static/data/'
ALLOWED_EXTENSIONS = {'zip'}
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from app import views

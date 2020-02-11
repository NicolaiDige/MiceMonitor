from app import application, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
import glob
import cv2
from flask import render_template, url_for, request
import sys
import os
import zipfile
import threading
import json

# Home page will display the ReadMe.txt file
@application.route('/', methods=['GET'])
def index():
    return render_template('index.html', record=0)

@application.route('/record', methods=['GET'])
def record():
    return render_template('index.html', record=1)

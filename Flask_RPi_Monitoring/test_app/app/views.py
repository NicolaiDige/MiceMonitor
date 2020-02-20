from app import application, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from flask import render_template, url_for, request

import glob
import sys
import os
import zipfile
import threading
import json
from time import sleep
from picamera import PiCamera

# Home page will display the ReadMe.txt file
@application.route('/', methods=['GET'])
def index():
    return render_template('index.html', record=0)

@application.route('/record', methods=['GET'])
def record():
    return render_template('index.html', record=1)

@application.route('/update', methods=['GET'])
def update_image():
    camera = PiCamera()
    camera.start_preview()
    sleep(2)
    camera.capture('/home/pi/MiceMonitor/Flask_RPi_Monitoring/test_app/app/static/images/Noir_image.jpg')
    camera.stop_preview()
    return render_template('index.html', record=1)

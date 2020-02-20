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

camera = PiCamera()
camera.sensor_mode=2
camera.sensor_mode=2
camera.resolution=(3280, 2464)
camera.framerate=15

# Home page will display the ReadMe.txt file
@application.route('/', methods=['GET'])
def index():
    return render_template('index.html', record=0)

@application.route('/record', methods=['GET'])
def record():
    return render_template('index.html', record=1)

@application.route('/update', methods=['GET'])
def update_image():
    sleep(0.5)
    camera.capture('/home/pi/MiceMonitor/Flask_RPi_Monitoring/test_app/app/static/images/Noir_image.jpg')
    return render_template('index.html', record=0)

@application.route('/vid_test', methods=['GET'])
def record_test():
    path = '/media/pi/Seagate Expansion Drive/ten_min_test.mjpg'
    camera.start_recording(path, format='mjpeg', bitrate=25000000)
    sleep(20)
    camera.stop_recording()
    return render_template('index.html', record=0)

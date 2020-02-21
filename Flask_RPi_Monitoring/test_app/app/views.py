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
import time

camera = PiCamera()
camera.resolution=(1296, 730)
camera.framerate=25

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
    sleep(1)
    return render_template('index.html', record=0)

@application.route('/vid_test', methods=['GET'])
def record_test():
    camera.start_preview()
    path = '/media/pi/Seagate Expansion Drive/ten_min_test.h264'
    path = '/home/pi/Desktop/ten_min_test_%d.h264'%(time.time())
    camera.start_recording(path, format='h264', intra_period=2, quality=30)
    camera.wait_recording(10)
    camera.stop_recording()
    camera.stop_preview()
    return render_template('index.html', record=0)

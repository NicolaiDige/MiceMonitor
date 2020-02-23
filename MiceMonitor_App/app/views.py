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
five_min_in_sec = 60*5.0

global record_active
record_active = False

def record_video(time_sec, video_name):
    global record_active
    dir = "/media/pi/Seagate Expansion Drive/%s"%(video_name)
    if not os.path.exists(dir):
        os.mkdir(dir)

    for i in range(0,int(time_sec/five_min_in_sec)):
        camera.start_preview()
        path = '%d/%s_%d-%dmin.h264'%(dir, video_name, i*5, (i+1)*5)
        camera.start_recording(path, format='h264', intra_period=0, quality=30)
        camera.wait_recording(5*60)
        camera.stop_recording()
        camera.stop_preview()

        if record_active==False:
            break
    record_active = False
    print("Recording stopped")


# Home page will display the ReadMe.txt file
@application.route('/', methods=['GET'])
def index():
    global record_active
    return render_template('index.html', record=0)

@application.route('/record', methods=['GET', 'POST'])
def record():
    time = request.form['record_time']
    name = request.form['record_name']
    time = [int(x) for x in time.split(":")]
    seconds = float(time[0]*60**2 + time[1]*60 + 60)
    record_active = True
    video_thread = threading.Thread(target=record_video, args=(seconds, name,))
    video_thread.start()

    return render_template('index.html', record=1)

@application.route('/stop_recording', methods=['GET'])
def stop_record():
    global record_active
    record_active = False
    return render_template('index.html', record=0)

@application.route('/update', methods=['GET'])
def update_image():
    sleep(0.5)
    print("doing the thing")
    camera.capture('/home/pi/MiceMonitor/Flask_RPi_Monitoring/test_app/app/static/images/Noir_image.jpg')
    sleep(0.5)
    return render_template('index.html', record=0)

@application.route('/vid_test', methods=['GET'])
def record_test():
    time_arg = float(request.args['time_min'])
    #camera.start_preview()
    """
    for i in range(int(time_arg/5.0)):
        camera.start_preview()
        print("Video number %d"%(i))
        path = '/media/pi/Seagate Expansion Drive/ten_min_test.h264'
        path = '/home/pi/Desktop/record_%d-%dmin_%d.h264'%(i*5, (i+1)*5, time.time())
        camera.start_recording(path, format='h264', intra_period=0, quality=30)
        camera.wait_recording(5*60)
        camera.stop_recording()
        camera.stop_preview()
    """

    # Insert conversion using method at
    # https://raspi.tv/2013/another-way-to-convert-raspberry-pi-camera-h264-output-to-mp4
    return render_template('index.html', record=0)

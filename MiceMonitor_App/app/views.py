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
        path = '%s/%s_%d-%dmin.h264'%(dir, video_name, i*5, (i+1)*5)
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

    if len(name) == 0 or len(time) == 0:
        return 404
    else:
        seconds = 0
        time = [int(x) for x in time.split(":")]
        time.reverse()
        for i in range(time):
            seconds += float(time[i]*60**i)
        record_active = True
        video_thread = threading.Thread(target=record_video, args=(seconds, name,))
        video_thread.start()

        return render_template('index.html', record=0)

@application.route('/stop_recording', methods=['GET'])
def stop_record():
    global record_active
    record_active = False
    return render_template('index.html', record=0)

@application.route('/update', methods=['GET'])
def update_image():
    sleep(0.5)
    print("doing the thing")
    camera.capture('/home/pi/MiceMonitor/MiceMonitor_App/app/static/images/Noir_image.jpg')
    sleep(0.5)
    return render_template('index.html', record=0)

@application.route('/convert_videos', methods=['GET'])
def convert_videos():
    videos = glob.glob("/media/pi/Seagate Expansion Drive/*/*.h264")
    videos = videos + glob.glob("/media/pi/Seagate Expansion Drive/*.h264")

    for video in videos:
        old_path = video
        new_path = video[:-5] + ".mp4"
        print("%s to %s"%(old_path, new_path))
        os.system("MP4Box -add \"%s\" \"%s\""%(old_path, new_path))
        os.system("rm \"%s\""%(old_path))

    print("\n-----\nConversion DONE!\n-----\n")

    return render_template('index.html', record=0)

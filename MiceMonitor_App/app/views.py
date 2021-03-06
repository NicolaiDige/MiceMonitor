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
from datetime import datetime

camera = PiCamera()
camera.resolution=(1296, 730)
camera.framerate=25
five_min_in_sec = 60*5.0
fifteen_min_in_sec = 60.0*15.0

global record_active
record_active = False

def record_video(time_sec, video_name):
    global record_active
    dir = "/media/pi/Seagate Expansion Drive/%s"%(video_name)
    if not os.path.exists(dir):
        os.mkdir(dir)

    file = open("%s/info.txt"%(dir), 'w+')
    file.write("Started at: %s\n"%(str(datetime.now())))

    for i in range(0,int(time_sec/fifteen_min_in_sec)):
        #camera.start_preview()
        path = '%s/%s_%.4d-%.4dmin.h264'%(dir, video_name, i*15, (i+1)*15)
        camera.start_recording(path, format='h264', intra_period=0, quality=30)
        for i in range(int((fifteen_min_in_sec)/2)):
            camera.wait_recording(2)
            if record_active==False:
                break
        camera.stop_recording()
        if record_active==False:
            break
        #camera.stop_preview()

    file.write("Stopped at: %s"%(str(datetime.now())))

    record_active = False
    print("Recording stopped")

# Home page will display the ReadMe.txt file
@application.route('/', methods=['GET'])
def index():
    global record_active
    return render_template('index.html', record=0)

@application.route('/record', methods=['GET', 'POST'])
def record():
    global record_active
    time = request.form['record_time']
    name = request.form['record_name']

    if len(name) == 0 or len(time) == 0:
        return 404
    else:
        seconds = 0
        time = [int(x) for x in time.split(":")]
        time.reverse()
        for i in range(len(time)):
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

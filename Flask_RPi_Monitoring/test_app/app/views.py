from app import application, auth, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
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
    im_paths = []
    sample_paths = glob.glob('app/static/data/*[!.zip]')
    sample_paths.sort(key=os.path.getmtime, reverse=True)
    for i, samp_path in enumerate(sample_paths):
        samp_files = glob.glob(samp_path + "/*")
        unproc_path = ""
        proc_path = ""

        for file in samp_files:
            if "_unprocessed.png" in file:
                unproc_path = file.replace("app/", "")
            elif "_processed.png" in file:
                proc_path = file.replace("app/", "")
            elif "info.json" in file:
                with open(file, 'r') as f:
                    info = json.load(f)[0]

        im_paths.append({
            'name': samp_path.split("/")[-1],
            'unproc_path' : unproc_path,
            'proc_path': proc_path,
            'proc_time': info['time'],
            'moving_cells': info['moving_cells'],
            'still_cells': info['still_cells']
            })

    return render_template('index.html', paths = im_paths, os_path =  os.path.abspath(os.getcwd()))

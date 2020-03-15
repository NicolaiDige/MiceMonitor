#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 20:00:29 2020

@author: nicolai
"""

import cv2
import numpy as np
from glob import glob
from subscripts.classes import movie_obj
from tqdm import tqdm
import matplotlib.pyplot as plt
import threading
import multiprocessing
import time
import pandas as pd

threading._shutdown()
"""
glob  -  Til at finde filer
pandas (også kaldet pd)  -  Til at arbejde med data og csv filer
cv2  -  Computer Vision 2, bruges til at arbejde med billeder og videoer
numpy (også kaldet np)  -  Bruges til at lave matematik i python (gennemsnit osv)
"""
fps = 25
n = 50
frame_in_vid = 30000
color_factor = 5
move_threshold_light = 15
move_threshold_dark = 8
save_every_x_image = 20
max_no_of_threads = 2
darkness_threshold = 50
datafile_output_ending = "_datafile.csv"
datafile_output_folder = "datafiles"

font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2
make_movies = True

def analyse_video(path):
    df_motion = pd.DataFrame({"Frame Number":[], "Time": [], "Image Mean": []})
    start_time = time.time()
    video_name = path.split("\\")[-1][:-4]
    cap = cv2.VideoCapture(path)
    no_of_frames = np.min([n+save_every_x_image*frame_in_vid, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))])
    counter = 0
    touch_counter = 2
    d = {}
    print(path)

    for index in range(no_of_frames):
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if index == 0:
            if np.mean(gray) < darkness_threshold:
                move_threshold = move_threshold_dark
            else:
                move_threshold = move_threshold_light

            background_images = np.repeat([gray], n, axis=0)
            background = np.median(background_images, axis=0)

            gray_motion = np.abs(gray-background)
            gray_motion[gray_motion<move_threshold] = 0

            if make_movies:
                frame_plus_motion = frame.copy().astype(np.float)
                frame_plus_motion[:,:,1] += (color_factor*gray_motion)
                frame_plus_motion[frame_plus_motion>255] = 255
                save_path = "processed_videos/" + video_name
                movie = movie_obj(save_path+"_colored", frame_plus_motion.astype(np.uint8), fps)
                gray_motion[gray_motion!=0] = 255
                movie_mot = movie_obj(save_path+"_motion", gray_motion.astype(np.uint8), fps)
            d["Frame Number"] = index
            d["Time"] = 0
            d["Image Mean"] = np.mean(gray_motion)
            df_motion = df_motion.append(d, ignore_index=True)
        else:
            if counter == n:
                counter = 0
            background_images[counter] = gray
            counter += 1

            if index > n and (index%save_every_x_image)==0:
                if np.mean(gray)<50:
                    move_threshold = move_threshold_dark
                else:
                    move_threshold = move_threshold_light

                background = np.median(background_images, axis=0)
                gray_motion = np.abs(gray-background)
                gray_motion[gray_motion<move_threshold] = 0

                if make_movies:
                    frame_plus_motion = frame.copy().astype(np.float)
                    frame_plus_motion[:,:,1] += (color_factor*gray_motion)
                    frame_plus_motion[frame_plus_motion>255] = 255

                    image = cv2.putText(frame_plus_motion, '%.2f'%(np.mean(gray)),
                        org, font,fontScale, color, thickness, cv2.LINE_AA)
                    movie.add_image(frame_plus_motion.astype(np.uint8))
                    gray_motion[gray_motion!=0] = 255
                    movie_mot.add_image(gray_motion.astype(np.uint8))
                d["Frame Number"] = index
                d["Time"] = index/25.0
                d["Image Mean"] = np.mean(gray_motion)
                df_motion = df_motion.append(d, ignore_index=True)
                print("%s/%s%s"%(datafile_output_folder,video_name,datafile_output_ending))
                df_motion.to_csv("%s/%s%s"%(datafile_output_folder,video_name,datafile_output_ending))

    if make_movies:
        movie.close_movie()
        movie_mot.close_movie()

        print("%s done in %.2f min"%(video_name, (time.time()-start_time)/60.0))
        cap.release()
    else:
        print("%s done in %.2f min"%(video_name, (time.time()-start_time)/60.0))
        cap.release()

video_paths = glob("analyse_files/*.mp4")
threads = []
time_start = time.time()
try:
    while len(video_paths) != 0 or len(threads) != 0:
        while len(threads) < max_no_of_threads and len(video_paths) != 0:
            t = threading.Thread(target=analyse_video, args=(video_paths[0],))
            threads.append(t)
            t.start()
            del video_paths[0]

        print("%d/%d (%.2f min)"%(
            len(threads),
            len(threads)+len(video_paths),
            (time.time()-time_start)/60.0))
        time.sleep(10)
        threads = [t for t in threads if t.isAlive()]
except:
    pass

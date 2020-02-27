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
global df_touches
if len(glob("touch_results.csv"))==1:
    df_touches = pd.read_csv("touch_results.csv")
else:
    df_touches = pd.DataFrame({"Video Name": []})

fps = 25
n = 50
frame_in_vid = 30000
color_factor = 5
move_threshold_light = 15
move_threshold_dark = 8
save_every_x_image = 20
max_no_of_threads = 2

darkness_threshold = 50

font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2
make_movies = False

def analyse_video(path):
    #print("thread %s started!"%(path.split("/")[-1]))
    global df_touches
    start_time = time.time()
    video_name = path.split("/")[-1][:-4]
    if not video_name in df_touches["Video Name"]:
        cap = cv2.VideoCapture(path)
        no_of_frames = np.min([n+save_every_x_image*frame_in_vid, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))])
        counter = 0
        touch_counter = 2
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
                    frame_plus_motion = frame.copy().astype(np.int32)
                    frame_plus_motion[:,:,1] += color_factor*gray_motion
                    frame_plus_motion[frame_plus_motion>255] = 255
                    frame_plus_motion = frame_plus_motion.astype(np.uint8)
                    save_path = "processed_videos/" + video_path
                    movie = movie_obj(save_path+"_colored", frame_plus_motion, fps)
                    gray_motion[gray_motion!=0] = 255
                    movie_mot = movie_obj(save_path+"_motion", gray_motion, fps)
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
                        frame_plus_motion = frame.copy().astype(np.int32)
                        frame_plus_motion[:,:,1] += color_factor*gray_motion
                        frame_plus_motion[frame_plus_motion>255] = 255
                        frame_plus_motion = frame_plus_motion.astype(np.uint8)

                        image = cv2.putText(frame_plus_motion, '%.2f'%(np.mean(gray)),
                            org, font,fontScale, color, thickness, cv2.LINE_AA)
                        movie.add_image(frame_plus_motion)
                        gray_motion[gray_motion!=0] = 255
                        movie_mot.add_image(gray_motion)
        if make_movies:
            movie.close_movie()
            movie_mot.close_movie()

        print("%s done in %.2f min"%(video_name, (time.time()-start_time)/60.0))
        df_touches = df_touches.append(
            {"Video Name":video_name, "Touch Count": touch_counter}, ignore_index=True)
        cap.release()
        df_touches.to_csv("touch_results.csv")

video_paths = glob("*.mp4")
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
        print(df_touches)
        time.sleep(10)
        threads = [t for t in threads if t.isAlive()]
except:
    df_touches.to_csv("touch_results.csv")
    pass

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
import threading
import time
import pandas as pd

threading._shutdown()
"""
glob  -  Til at finde filer
pandas (også kaldet pd)  -  Til at arbejde med data og csv filer
cv2  -  Computer Vision 2, bruges til at arbejde med billeder og videoer
numpy (også kaldet np)  -  Bruges til at lave matematik i python (gennemsnit osv)
"""

""" Change here for input video specifics """
video_paths = glob("analyse_files/*.mp4")
which_cam = "cam2" #ændre her i forhold til om det er cam1 eller cam2!
take_every_x_video = 2
input_video_fps = 25.0

focus_x_cam1 = [[145, 470], [140, 470], [132, 462], [505, 828], [495, 835], [505, 835]]
focus_y_cam1 = [[25, 230], [245, 455], [475, 690], [25, 230], [248, 465], [478, 708]]

focus_x_cam2 = [[560, 867], [534, 885], [537, 865], [924, 1273], [912, 1273], [903, 1263]]
focus_y_cam2 = [[46, 221], [251, 439], [460, 695], [40, 232], [265, 480], [490, 723]]

""" Change here for output video specifics """
save_every_x_image = 15 #
fps = 25 # how fast should the output videos be
frame_in_vid = 30000
color_factor = 20 # how much color should be in the coloured output video
datafile_output_ending = "_datafile.csv"
datafile_output_folder = "datafiles"

""" Change here for median filter specifics """
n = 100 # how far back should the filter look
use_every_x_frame = 8 # for the median filter
no_of_frames_in_array = n/use_every_x_frame
darkness_threshold = 50 # when does the light turn off
move_threshold_light = 15
move_threshold_dark = 5

""" Change here for analysing several videos simultaneously """
max_no_of_threads = 5

font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2
make_movies = True

""" Morphological operator settings to reduce noise (dont worry about it) """
do_morph_ops = True
kernel_size = 3
kernel = np.ones([kernel_size, kernel_size])
opening_iterations = 1
closing_iterations = 1

if which_cam.lower() == "cam1":
    focus_x = focus_x_cam1
    focus_y = focus_y_cam1
elif which_cam.lower() == "cam2":
    focus_x = focus_x_cam2
    focus_y = focus_y_cam2

def bright_or_dark(frame_gray):
    if np.mean(frame_gray) < darkness_threshold:
        return move_threshold_dark
    else:
        return move_threshold_light

def analyse_video(path):
    df_motion = pd.DataFrame({"Frame Number":[], "Time": []})
    start_time = time.time()
    video_name = path.split("\\")[-1][:-4]
    cap = cv2.VideoCapture(path)
    no_of_frames = np.min([n+save_every_x_image*frame_in_vid, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))])
    d = {}
    print("Video %s is now being analysed"%(path))

    for index in range(no_of_frames):
        ret, frame = cap.read()

        # If the first frame
        if index == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Check if light is on in room
            move_threshold = bright_or_dark(gray)

            # Initiate the background_images array
            background_images = np.array([gray])

            # Find its median
            background = background_images[0]

            # First frame is purely black
            gray_motion = np.zeros(gray.shape)

            # Make the first frame for the coloured movie
            frame_plus_motion = frame.copy().astype(np.float)

            # Initiate the movie files
            save_path = "processed_videos/" + video_name
            movie = movie_obj(save_path+"_colored", frame_plus_motion.astype(np.uint8), fps)
            movie_mot = movie_obj(save_path+"_motion", gray_motion.astype(np.uint8), fps)

            # Make the first datarow for the csv datafile
            d["Frame Number"] = index
            d["Time"] = 0

            # Process all the defined areas
            for i in range(len(focus_x)):
                focus_area = gray_motion[focus_y[i][0]:focus_y[i][1], focus_x[i][0]:focus_x[i][1]]
                d["Image Mean Box %d"%(i)] = np.mean(focus_area)

            # Add datarow to the dataframe
            df_motion = df_motion.append(d, ignore_index=True)

        # If not the first frame
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Check if you should add another frame to the background_images array
            if index%use_every_x_frame == 0:
                background_images = np.append(background_images, [gray], 0)

                # If you too many images in background_images, remove the oldest frame
                if background_images.shape[0]>no_of_frames_in_array:
                    background_images = background_images[1:]

           # Check if you should process the frame at hand
            if (index%save_every_x_image)==0:
                # Check if light is on in room
                move_threshold = bright_or_dark(gray)

                # Find background by taking the median of previous frames
                background = np.median(background_images, axis=0)

                # Subtract the background from the current image to find differences
                gray_motion = np.abs(gray-background)

                # If differences are small, set them to zero, otherwise 255
                gray_motion[gray_motion<move_threshold] = 0
                gray_motion[gray_motion!=0] = 255

                # This is to reduce little noise speckles
                if do_morph_ops:
                    closing = cv2.morphologyEx(gray_motion, cv2.MORPH_CLOSE, kernel, iterations=closing_iterations)
                    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel, iterations=opening_iterations)
                    gray_motion = opening

                # Make the frame for the coloured movie, and add threshold value
                # in top corner
                frame_plus_motion = frame.copy().astype(np.float)
                frame_plus_motion[:,:,1] += (color_factor*gray_motion)
                frame_plus_motion[frame_plus_motion>255] = 255

                # Add processed frames to the movies
                movie.add_image(frame_plus_motion.astype(np.uint8))
                movie_mot.add_image(gray_motion.astype(np.uint8))

                # Add data to a new datarow
                d["Frame Number"] = index
                d["Time"] = index/input_video_fps

                # Process all the defined areas
                for i in range(len(focus_x)):
                    focus_area = gray_motion[focus_y[i][0]:focus_y[i][1], focus_x[i][0]:focus_x[i][1]]
                    d["Image Mean Box %d"%(i)] = np.mean(focus_area)

                # Add datarow to the dataframe and save the temporary datafile
                df_motion = df_motion.append(d, ignore_index=True)
                df_motion.to_csv("%s/%s%s"%(datafile_output_folder,video_name,datafile_output_ending))

    # Close the opened video file
    cap.release()

    # If movies were made, close them before exiting
    if make_movies:
        movie.close_movie()
        movie_mot.close_movie()
        print("%s done in %.2f min"%(video_name, (time.time()-start_time)/60.0))
    else:
        cap.release()
        print("%s done in %.2f min"%(video_name, (time.time()-start_time)/60.0))


""" Here is the code that runs the "analyse_video" function on all videos in folder """

# Here some of the video paths are put away in order to only analyse some of the videos
datafile_paths = glob('datafiles/*/*.csv')
for i in range(len(datafile_paths)):
    temp = datafile_paths[i]
    temp = temp.replace('_datafile.csv', '').split("\\")[-1]
    datafile_paths[i] = temp

print("Starting")
choices = np.arange(0, len(video_paths), take_every_x_video)
new_video_paths = []
for i in choices:
    temp = video_paths[i].replace('.mp4', '').split("\\")[-1]
    if not temp in datafile_paths:
        new_video_paths.append(video_paths[i])
        
if len(new_video_paths) == 0:
    print("No new videos to analyse")
video_paths = new_video_paths

threads = []
time_start = time.time()

# While some paths are remaining, or some of the threads are still running
while len(video_paths) != 0 or len(threads) != 0:

    # While there are more paths, and the maximum number of threads are not started
    while len(threads) < max_no_of_threads and len(video_paths) != 0:
        # Start a thread that runs the "analyse_video" function on the video_path
        # next in line
        t = threading.Thread(target=analyse_video, args=(video_paths[0],))
        threads.append(t)
        t.start()

        # Remove the video path so the next thread will take the next in line
        del video_paths[0]

    # Print a status of the threads
    print("%d/%d (%.2f min)"%(
        len(threads),
        len(threads)+len(video_paths),
        (time.time()-time_start)/60.0))
    time.sleep(10)
    threads = [t for t in threads if t.is_alive()]
print("Finished")

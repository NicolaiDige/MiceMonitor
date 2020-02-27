import time
import cv2

class movie_obj:
    def __init__(self, movie_path, first_image, fps=25):
        self.path = movie_path
        try:
            height, width, channels = first_image.shape
            is_color = True
        except:
            height, width = first_image.shape
            is_color = False

        size = (width,height)
        self.out = cv2.VideoWriter(movie_path + ".mp4",
                                   cv2.VideoWriter_fourcc(*'mp4v'),
                                   fps,
                                   size,
                                   is_color)
        self.out.write(first_image)

    def add_image(self, image):
        self.out.write(image)

    def close_movie(self):
        self.out.release()

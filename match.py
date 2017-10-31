import cv2
import os
import MySQLdb
import numpy as np
from matplotlib import pyplot as plt

conn = MySQLdb.connect(host="a01-docker-01", user="root", passwd="q1w2e3r4", db="intelligence")
x = conn.cursor()

template = cv2.imread('template.jpg',0)
w, h = template.shape[::-1]

for filename in os.listdir('test/data/l-_NYHkKdwQ/'):
    if filename.endswith(".jpg"):
        img = cv2.imread('test/data/l-_NYHkKdwQ/' + filename, 0)
        img2 = img.copy()

        # All the 6 methods for comparison in a list
        methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
                    'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

        for meth in methods:
            img = img2.copy()
            method = eval(meth)

            # Apply template Matching
            res = cv2.matchTemplate(img,template,method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            min_x, min_y = min_loc
            max_x, max_y = max_loc

            print min_val

            query = "INSERT INTO image_matches (filename, method, min_val, min_x, min_y, max_val, max_x, max_y) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            args = (filename, meth, min_val, min_x, min_y, max_val, max_x, max_y)
            x.execute(query, args)
            #conn.commit()

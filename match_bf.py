import cv2
import os
import MySQLdb
import datetime
import numpy as np
from matplotlib import pyplot as plt

conn = MySQLdb.connect(host="a01-docker-01", user="root", passwd="q1w2e3r4", db="intelligence")
x = conn.cursor()

img1 = cv2.imread('template.jpg', 0)          # queryImage

# Initiate ORB detector
orb = cv2.ORB()

print datetime.datetime.now()

filelist = os.listdir('test/data/l-_NYHkKdwQ/')
for filename in sorted(filelist):
    if filename.endswith(".jpg"):
        img2 = cv2.imread('test/data/l-_NYHkKdwQ/' + filename, 0) # trainImage

        # find the keypoints and descriptors with ORB
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        # create BFMatcher object
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # Match descriptors.
        matches = bf.match(des1, des2)

        # Sort them in the order of their distance.
        matches = sorted(matches, key = lambda x:x.distance)

        print filename, matches[0].distance, matches[0].trainIdx, matches[0].queryIdx, matches[0].imgIdx

        query = "INSERT INTO image_matches_bf (filename, distance, trainIdx, queryIdx, imgIdx) VALUES (%s, %s, %s, %s, %s)"
        args = (filename, matches[0].distance, matches[0].trainIdx, matches[0].queryIdx, matches[0].imgIdx)
        x.execute(query, args)
        #conn.commit()

import cv2
import os
import MySQLdb
import datetime
import sys
import numpy as np
from matplotlib import pyplot as plt

if len(sys.argv) != 4:
    print "Incorrect number of arguments.  Need request_id, source_image, youtube_path"
    exit(1)

_, request_id, source_image, youtube_path = sys.argv

if not os.path.isfile(source_image):
    print "Source image does not exist."
    exit(1)

if not os.path.isdir(youtube_path):
    print "YouTube path does not exist."
    exit(1)

youtube_path = os.path.join(youtube_path, '') # ensures a trailing slash
youtube_id = os.path.basename(os.path.normpath(youtube_path))

conn = MySQLdb.connect(host="a01-mysql-01", user="root", passwd="q1w2e3r4", db="image_match")
x = conn.cursor()

img1 = cv2.imread(source_image, 0)          # queryImage

# Initiate ORB detector
orb = cv2.ORB()

print datetime.datetime.now()

filelist = os.listdir(youtube_path)
for filename in sorted(filelist):
    if filename.endswith(".jpg"):
        img2 = cv2.imread(youtube_path + filename, 0) # trainImage

        frame, ext = filename.split(".")

        #print filename

        try:
            # find the keypoints and descriptors with ORB
            kp1, des1 = orb.detectAndCompute(img1, None)
            kp2, des2 = orb.detectAndCompute(img2, None)

            # create BFMatcher object
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

            # Match descriptors.
            matches = bf.match(des1, des2)

            # Sort them in the order of their distance.
            matches = sorted(matches, key = lambda x:x.distance)

            #print youtube_id, frame, matches[0].distance, matches[0].trainIdx, matches[0].queryIdx, matches[0].imgIdx

            query = "INSERT INTO image_matches_bf (video_id, request_id, frame, filename, distance, trainIdx, queryIdx, imgIdx) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            args = (youtube_id, request_id, frame, filename, matches[0].distance, matches[0].trainIdx, matches[0].queryIdx, matches[0].imgIdx)
            x.execute(query, args)
            #conn.commit()

        except:
            query = "INSERT INTO image_matches_bf (video_id, request_id, frame, filename) VALUES (%s, %s, %s, %s)"
            args = (youtube_id, request_id, frame, filename)
            x.execute(query, args)

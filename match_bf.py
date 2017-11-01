import cv2
import os
import MySQLdb
import datetime
import sys
import time
import socket
import numpy as np
from matplotlib import pyplot as plt

conn = MySQLdb.connect(host="a01-mysql-01", user="root", passwd="q1w2e3r4", db="image_match")
conn.autocommit(True)
x = conn.cursor()

while True:
    x.execute("SELECT task_id, guid, video_id, template FROM tasks WHERE started IS NULL LIMIT 1")
    if x.rowcount == 1:
        break
    time.sleep(5)
    print "Nothing to do"

row = x.fetchone()

task_id = row[0]
task_guid = row[1]
youtube_id = row[2]
youtube_path = "test/data/" + youtube_id + "/"
source_image = "templates/" + row[3]

query = "UPDATE tasks SET worker_host = %s, started = %s WHERE task_id = %s LIMIT 1"
print query, socket.gethostname(), time.strftime('%Y-%m-%d %H:%M:%S'), task_id
args = (socket.gethostname(), time.strftime('%Y-%m-%d %H:%M:%S'), task_id)
x.execute(query, args)

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
            args = (youtube_id, task_id, frame, filename, matches[0].distance, matches[0].trainIdx, matches[0].queryIdx, matches[0].imgIdx)
            x.execute(query, args)
            #conn.commit()

        except Exception, e:
            print str(e)
            print "Exception: ", youtube_path, filename, source_image, task_id, frame, filename
            query = "INSERT INTO image_matches_bf (video_id, request_id, frame, filename) VALUES (%s, %s, %s, %s)"
            args = (youtube_id, task_id, frame, filename)
            x.execute(query, args)

query = "UPDATE tasks SET completed = %s WHERE task_id = %s LIMIT 1"
print query, socket.gethostname(), time.strftime('%Y-%m-%d %H:%M:%S'), task_id
args = (time.strftime('%Y-%m-%d %H:%M:%S'), task_id)
x.execute(query, args)

print "done!"

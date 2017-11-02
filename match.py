import cv2
import os
import MySQLdb
import datetime
import sys
import signal
import time
import socket
import numpy as np
from matplotlib import pyplot as plt

conn = MySQLdb.connect(host="a01-mysql-01", user="root", passwd="q1w2e3r4", db="image_match")
conn.autocommit(True)
x = conn.cursor()

def signal_handler(signal, frame):
        print('Shuting down...')
        global task_id, conn, x
        print task_id

        query = "DELETE FROM image_matches_bf WHERE task_id = %s"
        args = (task_id)
        x.execute(query, args)

        query = "UPDATE tasks SET worker_host = null, started = null, completed = null WHERE task_id = %s LIMIT 1"
        args = (task_id)
        x.execute(query, args)

        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

while True:
    x.execute("SELECT task_id, guid, video_id, template FROM tasks WHERE started IS NULL LIMIT 1")
    if x.rowcount == 1:
        break
    time.sleep(5)

row = x.fetchone()

task_id = row[0]
task_guid = row[1]
youtube_id = row[2]
youtube_path = "data/frames/" + youtube_id + "/"
source_image = "data/templates/" + row[3]

query = "UPDATE tasks SET worker_host = %s, started = %s WHERE task_id = %s LIMIT 1"
args = (socket.gethostname(), time.strftime('%Y-%m-%d %H:%M:%S'), task_id)
x.execute(query, args)

img1 = cv2.imread(source_image, 0)          # queryImage

# Initiate ORB detector
orb = cv2.ORB()

start_time = time.time()
print "Picking up task: ", task_id, task_guid, youtube_id

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

            if matches[0].distance < 26: # only saving matches now
                query = "INSERT INTO image_matches_bf (video_id, task_id, frame, filename, distance, trainIdx, queryIdx, imgIdx) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                args = (youtube_id, task_id, frame, filename, matches[0].distance, matches[0].trainIdx, matches[0].queryIdx, matches[0].imgIdx)
                x.execute(query, args)
                #conn.commit()

        except Exception, e:
            print str(e)
            print "Exception: ", youtube_path, filename, source_image, task_id, frame, filename
            query = "INSERT INTO image_matches_bf (video_id, task_id, frame, filename) VALUES (%s, %s, %s, %s)"
            args = (youtube_id, task_id, frame, filename)
            x.execute(query, args)

query = "UPDATE tasks SET completed = %s WHERE task_id = %s LIMIT 1"
args = (time.strftime('%Y-%m-%d %H:%M:%S'), task_id)
x.execute(query, args)

run_time = (time.time() - start_time) / 60
print "Finished task:   ", task_id, task_guid, youtube_id, run_time, " min"

# allowing the script to die, respawned by match_forever.sh or restart options in docker-compose if running in prod

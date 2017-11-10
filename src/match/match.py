import cv2
import os
import os.path
import MySQLdb
import datetime
import sys
import signal
import time
import socket
import numpy as np
from functools import partial
from matplotlib import pyplot as plt

def signal_handler(task_id, x, conn, signal, frame, dl_required):
        print('Shuting down...')

        query = "DELETE FROM image_matches_bf WHERE task_id = " + str(task_id)
        x.execute(query)
        query = "UPDATE tasks SET worker_host = null, started = null, completed = null WHERE task_id = " + str(task_id) + " LIMIT 1"
        x.execute(query)

        if video_id != "" and dl_required:
            os.system("rm -f data/frames/" + video_id + "/*.jpg")
            os.system("rmdir data/frames/" + video_id)

        sys.exit(0)

conn = MySQLdb.connect(host="a01-mysql-01", user="root", passwd="q1w2e3r4", db="image_match")
conn.autocommit(True)
x = conn.cursor()

dirs = next(os.walk('data/frames'))[1]
dir_list = "'" + "', '".join(dirs) + "'"

while True:
    # first try to pickup a task where we hold the frames
    sql = "SELECT task_id, guid, video_id, template FROM tasks WHERE started IS NULL && video_id IN (" + dir_list + ") LIMIT 1"
    x.execute(sql)
    if x.rowcount == 1:
        dl_required = False
        break

    # if there are no tasks available, offer to pickup one that requires a rsync
    sql = "SELECT task_id, guid, video_id, template FROM tasks WHERE started IS NULL LIMIT 1"
    x.execute(sql)
    if x.rowcount == 1:
        dl_required = True
        break

    time.sleep(5)

row = x.fetchone()

task_id = row[0]
task_guid = row[1]
video_id = row[2]
video_path = "data/frames/" + video_id + "/"
source_image = "/tmp/" + row[3]
exceptions = 0

if os.path.isfile("/etc/docker_hostname"):
    hostname = open("/etc/docker_hostname").read()
    hostname = hostname.strip()
    container = socket.gethostname()
else:
    hostname = socket.gethostname()
    container = None

query = "UPDATE tasks SET worker_host = %s, container = %s, started = %s WHERE task_id = %s LIMIT 1"
args = (hostname, container, time.strftime('%Y-%m-%d %H:%M:%S'), task_id)
x.execute(query, args)

start_time = time.time()
print "Picking up task: ", task_id, task_guid, video_id

signal.signal(signal.SIGINT, partial(signal_handler, task_id, x, conn, dl_required))
signal.signal(signal.SIGTERM, partial(signal_handler, task_id, x, conn, dl_required))

if dl_required:
    # fetch copy of frames
    print "[{0}] Copying frames from master...".format(video_id)
    os.system("rsync -a andrew@server-13:/home/andrew/go/src/github.com/atw527/image-match/data/frames/ data/frames/{0}".format(video_id))

# fetch template image
print "[{0}] Copying image template from master...".format(video_id)
os.system("wget -O /tmp/" + row[3] + " http://server-13:8088/templates/" + row[3])
img1 = cv2.imread(source_image, 0)          # queryImage

# Initiate ORB detector
orb = cv2.ORB()

filelist = os.listdir(video_path)
for filename in sorted(filelist):
    if filename.endswith(".jpg"):
        img2 = cv2.imread(video_path + filename, 0) # trainImage

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

            #print video_id, frame, matches[0].distance, matches[0].trainIdx, matches[0].queryIdx, matches[0].imgIdx

            if matches[0].distance < 26: # only saving matches now
                query = "INSERT INTO image_matches_bf (video_id, task_id, frame, filename, distance, trainIdx, queryIdx, imgIdx) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                args = (video_id, task_id, frame, filename, matches[0].distance, matches[0].trainIdx, matches[0].queryIdx, matches[0].imgIdx)
                x.execute(query, args)
                #conn.commit()

        except Exception, e:
            print str(e)
            print "Exception: ", video_path, filename, source_image, task_id, frame, filename
            exceptions = exceptions + 1
            #query = "INSERT INTO image_matches_bf (video_id, task_id, frame, filename) VALUES (%s, %s, %s, %s)"
            #args = (video_id, task_id, frame, filename)
            #x.execute(query, args)

# cleaning up
print "[{0}] Cleaning up...".format(video_id)
if video_id != "" and dl_required:
    os.system("rm -f data/frames/" + video_id + "/*.jpg")
    os.system("rmdir data/frames/" + video_id)

query = "UPDATE tasks SET completed = %s, exceptions = %s WHERE task_id = %s LIMIT 1"
args = (time.strftime('%Y-%m-%d %H:%M:%S'), exceptions, task_id)
x.execute(query, args)

run_time = (time.time() - start_time) / 60
print "Finished task:   ", task_id, task_guid, video_id, run_time, " min"

# allowing the script to die, respawned by match_forever.sh or restart options in docker-compose if running in prod

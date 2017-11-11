import cv2
import os
import os.path
import MySQLdb
import datetime
import sys
import signal
import time
import socket
import commands
import numpy as np
from functools import partial
from matplotlib import pyplot as plt

def fail_log(task_id, video_id, dl_required, notes):
    # had a critical failure; log some stuff and shutdown
    if video_id != "" and dl_required:
        os.system("rm -f data/frames/" + video_id + "/*.jpg")
        os.system("rmdir data/frames/" + video_id)

    query = "DELETE FROM matches WHERE task_id = {0}".format(task_id)
    cur.execute(query)

    query = "UPDATE tasks SET completed = %s, notes = %s WHERE task_id = %s LIMIT 1"
    args = (time.strftime('%Y-%m-%d %H:%M:%S'), notes, task_id)
    cur.execute(query, args)

    sys.exit(1)

def signal_handler(task_id, cur, conn, dl_required, signal, frame):
    print('Shuting down...')

    query = "DELETE FROM matches WHERE task_id = " + str(task_id)
    cur.execute(query)
    query = "UPDATE tasks SET host = null, started = null, completed = null WHERE task_id = " + str(task_id) + " LIMIT 1"
    cur.execute(query)

    if video_id != "" and dl_required:
        os.system("rm -f data/frames/" + video_id + "/*.jpg")
        os.system("rmdir data/frames/" + video_id)

    sys.exit(0)

# verify/make the env var sane
ENV_MASTER     = os.getenv('MASTER', 'server-13')
ENV_MYSQL_HOST = os.getenv('MYSQL_HOST', 'a01-mysql-01')
ENV_MYSQL_PORT = os.getenv('MYSQL_PORT', 3306)
ENV_MYSQL_DB   = os.getenv('MYSQL_DB', 'image_match')
ENV_MYSQL_USER = os.getenv('MYSQL_USER', 'root')
ENV_MYSQL_PASS = os.getenv('MYSQL_PASS', 'q1w2e3r4')

# try to figure out our current situation
if os.path.isdir("/usr/local/data"):
    print "I think I'm in a docker container"
    os.chdir("/usr/local/data")
elif os.path.isdir("/home/andrew/go/src/github.com/atw527/image-match/data"):
    print "I think I'm being ran locally"
    os.chdir("/home/andrew/go/src/github.com/atw527/image-match/data")
else:
    print "Cannot find working directory!"
    sys.exit(1)

# get the hostname(s)
if os.path.isfile("/etc/docker_hostname"):
    hostname = open("/etc/docker_hostname").read()
    hostname = hostname.strip()
    container = socket.gethostname()
else:
    hostname = socket.gethostname()
    container = None

# determine if master/slave
if ENV_MASTER == hostname:
    print "I am MASTER!"
    is_master = True
else:
    print "I am slave"
    is_master = False

# ready to roll, connect to DB
conn = MySQLdb.connect(host=ENV_MYSQL_HOST, user=ENV_MYSQL_USER, passwd=ENV_MYSQL_PASS, db=ENV_MYSQL_DB)
conn.autocommit(True)
cur = conn.cursor()

dirs = next(os.walk('frames'))[1]
dir_list = "'" + "', '".join(dirs) + "'"

while True:
    # first try to pickup a task where we hold the frames
    sql = "SELECT task_id, guid, video_id, template FROM tasks WHERE started IS NULL && video_id IN (" + dir_list + ") LIMIT 1"
    cur.execute(sql)
    if cur.rowcount == 1:
        dl_required = False
        break

    # if there are no tasks available, offer to pickup one that requires a rsync
    sql = "SELECT task_id, guid, video_id, template FROM tasks WHERE started IS NULL LIMIT 1"
    cur.execute(sql)
    if cur.rowcount == 1:
        dl_required = True
        break

    time.sleep(5)

row = cur.fetchone()

task_id = row[0]
task_guid = row[1]
video_id = row[2]
video_path = "frames/" + video_id + "/"
source_image = "/tmp/" + row[3]
exceptions = 0

if os.path.isfile("/etc/docker_hostname"):
    hostname = open("/etc/docker_hostname").read()
    hostname = hostname.strip()
    container = socket.gethostname()
else:
    hostname = socket.gethostname()
    container = None

query = "UPDATE tasks SET host = %s, container = %s, started = %s WHERE task_id = %s LIMIT 1"
args = (hostname, container, time.strftime('%Y-%m-%d %H:%M:%S'), task_id)
cur.execute(query, args)

start_time = time.time()
print "Picking up task: ", task_id, task_guid, video_id

signal.signal(signal.SIGINT, partial(signal_handler, task_id, cur, conn, dl_required))
signal.signal(signal.SIGTERM, partial(signal_handler, task_id, cur, conn, dl_required))

if dl_required:
    # fetch copy of frames
    print "[{0}] Copying frames from master...".format(video_id)
    cmd = "rsync -a andrew@{0}:/home/andrew/go/src/github.com/atw527/image-match/data/frames/{1} frames/".format(ENV_MASTER, video_id)
    (return_val, output) = commands.getstatusoutput(cmd)
    if return_val != 0:
        fail_log(task_id, video_id, dl_required, cmd + output)

# fetch template image
print "[{0}] Copying image template from master...".format(video_id)
os.system("rm -f /tmp/" + row[3])
(return_val, output) = commands.getstatusoutput("wget -O /tmp/{0} http://{1}:8088/data/templates/{0}".format(row[3], ENV_MASTER))
if return_val != 0:
    fail_log(task_id, video_id, dl_required, output)

img1 = cv2.imread(source_image, 0)
orb = cv2.ORB()

print "[{0}] Starting the match process...".format(video_id)

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
                query = "INSERT INTO matches (video_id, task_id, frame, filename, distance, trainIdx, queryIdx, imgIdx) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                args = (video_id, task_id, frame, filename, matches[0].distance, matches[0].trainIdx, matches[0].queryIdx, matches[0].imgIdx)
                cur.execute(query, args)
                #conn.commit()

        except Exception, e:
            print str(e)
            print "Exception: ", video_path, filename, source_image, task_id, frame, filename
            exceptions = exceptions + 1
            #query = "INSERT INTO matches (video_id, task_id, frame, filename) VALUES (%s, %s, %s, %s)"
            #args = (video_id, task_id, frame, filename)
            #cur.execute(query, args)

# cleaning up
print "[{0}] Cleaning up...".format(video_id)
if video_id != "" and dl_required:
    os.system("rm -f data/frames/" + video_id + "/*.jpg")
    os.system("rmdir data/frames/" + video_id)

query = "UPDATE tasks SET completed = %s, exceptions = %s WHERE task_id = %s LIMIT 1"
args = (time.strftime('%Y-%m-%d %H:%M:%S'), exceptions, task_id)
cur.execute(query, args)

run_time = (time.time() - start_time) / 60
print "Finished task:   ", task_id, task_guid, video_id, run_time, " min"

# allowing the script to die, respawned by match_forever.sh or restart options in docker-compose if running in prod

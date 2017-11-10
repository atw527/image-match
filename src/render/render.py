import os
import os.path
import MySQLdb
import datetime
import sys
import signal
import time
import socket
import commands
import re
import numpy as np
from functools import partial
from random import randint

def signal_handler(video_id, x, conn, signal, frame):
        print('Shuting down...')

        # put the item we were working on back in the queue for someone else to pick up
        query = "UPDATE encode SET host = null, container = null WHERE video_id = '{0}' LIMIT 1".format(video_id)
        x.execute(query)

        # delete any progress we made on the task
        if video_id != "":
            os.system("rm -f frames/" + video_id + "/*.jpg")
            os.system("rmdir frames/" + video_id)
            os.system("rm -f video/" + video_id + "*")

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
if os.environ['MASTER'] == hostname:
    print "I am MASTER!"
    is_master = True
else:
    print "I am slave"
    print "This module is designed for the master node only."
    is_master = False
    exit(1)

# ready to roll, connect to DB
conn = MySQLdb.connect(host=ENV_MYSQL_HOST, user=ENV_MYSQL_USER, passwd=ENV_MYSQL_PASS, db=ENV_MYSQL_DB)
conn.autocommit(True)
x = conn.cursor()

# wait patiently for something to do
while True:
    time.sleep(randint(5,10))
    sql = "SELECT video_id FROM render WHERE host IS NULL LIMIT 1"
    x.execute(sql)
    if x.rowcount == 1:
        break

row = x.fetchone()
video_id = row[0]

query = "UPDATE render SET host = %s, container = %s WHERE video_id = %s LIMIT 1"
args = (hostname, container, video_id)
x.execute(query, args)

print "[{0}] Picking up task.".format(video_id)

# now is when we care if the script is killed
signal.signal(signal.SIGINT, partial(signal_handler, video_id, x, conn))
signal.signal(signal.SIGTERM, partial(signal_handler, video_id, x, conn))

if !is_master:
    print "[{0}] Cleaning local folders and pulling MP4...".format(video_id)

    # hoping for a return_val of 23 (file not found), will get 0 if found
    (return_val, output) = commands.getstatusoutput("rsync andrew@{0}:/home/andrew/go/src/github.com/atw527/image-match/data/frames/{1} /tmp/".format(ENV_MASTER, video_id))
    if return_val == 0:
        print "[{0}] Frames directory found on master!  Skipping.".format(video_id)
        query = "UPDATE render SET completed = %s, notes = %s WHERE video_id = %s LIMIT 1"
        args = (time.strftime('%Y-%m-%d %H:%M:%S'), "skipped", video_id)
        x.execute(query, args)
        exit(0)

    if video_id != "":
        os.system("rm -f frames/" + video_id + "/*.jpg")
        os.system("rmdir frames/" + video_id)
        os.system("rm -f video/" + video_id + "*")

    (return_val, output) = commands.getstatusoutput("rsync andrew@{0}:/home/andrew/go/src/github.com/atw527/image-match/data/video/{1}* video/".format(ENV_MASTER, video_id))
else:
    # master has to check if the frame dir exists locally (also reasons to skip)
    if os.path.isdir("frames/{0}".format(video_id)):
        print "[{0}] Frames directory found!  Skipping.".format(video_id)
        query = "UPDATE render SET completed = %s, notes = %s WHERE video_id = %s LIMIT 1"
        args = (time.strftime('%Y-%m-%d %H:%M:%S'), "skipped", video_id)
        x.execute(query, args)
        exit(0)

# extract the frames
print "[{0}] Extracting frames...".format(video_id)
os.system("mkdir frames/{0}".format(video_id));
os.system("ffmpeg -i video/{0}.mp4 -r 10/1 -f image2 frames/{0}/%6d.jpg > /dev/null".format(video_id));

# dedup
print "[{0}] Running dedup...".format(video_id)

os.chdir("frames/{0}".format(video_id))

frames = sorted(os.listdir("."))
frame_count = len(frames)

x = 0
y = 1
exceptions = 0
while True:
    try:
        if y > frame_count - 5 or x > frame_count - 5:
            break

        (return_val, output) = commands.getstatusoutput("compare -metric RMSE {0} {1} NULL: 2>&1".format(frames[x], frames[y]))
        diff = int(re.search('[0-9]+', output).group())

        if diff < 5000 and diff != 0:
            # frame is similar enough to remove
            os.remove(frames[y])
            #print "[del] {0}".format(frames[y]), return_val, diff, output
            y += 1
        else:
            # frame has changed, set this as the new starting point
            x = y
            y += 1

    except Exception, e:
        print str(e)
        # reset the frame indexes to try to get out of this exception
        x = y
        y += 1
        exceptions += 1
        continue

os.chdir("../../")

if !is_master:
    print "[{0}] Copying frames back to {1}...".format(video_id, ENV_MASTER)
    os.system("rsync -a --delete-excluded frames/{0} andrew@{1}:/home/andrew/go/src/github.com/atw527/image-match/data/frames/".format(video_id), ENV_MASTER)

    # cleaning up
    print "[{0}] Cleaning up...".format(video_id)
    if video_id != "":
        os.system("rm -f frames/" + video_id + "/*.jpg")
        os.system("rmdir frames/" + video_id)
        os.system("rm -f video/" + video_id + "*")

query = "UPDATE render SET completed = %s, exceptions = %s WHERE video_id = %s LIMIT 1"
args = (time.strftime('%Y-%m-%d %H:%M:%S'), exceptions, video_id)
x.execute(query, args)

print "[{0}] Done!".format(video_id)

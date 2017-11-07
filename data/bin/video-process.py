import os
import os.path
import MySQLdb
import datetime
import sys
import signal
import time
import socket
import subprocess
import re
import numpy as np
from functools import partial

def signal_handler(video_id, x, conn, signal, frame):
        print('Shuting down...')

        # put the item we were working on back in the queue for someone else to pick up
        query = "UPDATE encode SET host = null WHERE video_id = " + video_id + " LIMIT 1"
        x.execute(query)

        # delete any progress we made on the task
        if video_id != "":
            os.system("rm -f frames/" + video_id + "/*.jpg")
            os.system("rmdir " + video_id)
            os.system("rm -f video/" + video_id + "*")

        sys.exit(0)

conn = MySQLdb.connect(host="a01-mysql-01", user="root", passwd="q1w2e3r4", db="image_match")
conn.autocommit(True)
x = conn.cursor()

while True:
    time.sleep(5)
    sql = "SELECT video_id FROM encode WHERE host IS NULL LIMIT 1"
    x.execute(sql)
    if x.rowcount == 1:
        break

row = x.fetchone()
video_id = row[0]

os.chdir(os.path.dirname(sys.argv[0]))
os.chdir("..")

if os.path.isfile("/etc/docker_hostname"):
    hostname = open("/etc/docker_hostname").read()
    container = socket.gethostname()
else:
    hostname = socket.gethostname()
    container = ""

query = "UPDATE tasks SET host = %s, container = %s WHERE video_id = %s LIMIT 1"
args = (hostname, container, video_id)
x.execute(query, args)

print "Picking up task: ", video_id

# now is when we care if the script is killed
signal.signal(signal.SIGINT, partial(signal_handler, video_id, x, conn))
signal.signal(signal.SIGTERM, partial(signal_handler, video_id, x, conn))

# sync the file from server-13
print "Pulling MP4...", video_id
os.system("rsync andrew@server-13:/home/andrew/go/src/github.com/atw527/image-match/data/video/{0}* video/".format(video_id))

# extract the frames
print "Extracting frames...", video_id
os.system("mkdir frames/{0}".format(video_id));
os.system("ffmpeg -i video/{0}.mp4 -r 10/1 -f image2 frames/{0}/%6d.jpg > /dev/null".format(video_id));

# dedup
print "Running dedup...", video_id
frames = os.listdir("frames/{0}".format(video_id))

for x in range(0, len(frames) - 1):
    for y in range(x + 1, len(frames)):
        output = subprocess.check_output("compare -metric RMSE {0} {1} NULL: 2>&1".format(frames[x], frames[y]), shell=True)
        diff = int(re.search('[0-9]+', output).group())

        if diff < 5000 && diff != 0:
            os.remove("frames/{0}.jpg".format(frames[y]))
        else:
            x = y
            break

# copy frames back to server-13
print "Copying frames back to server-13...", video_id
os.system("rsync -a frames/{0} andrew@server-13:/home/andrew/go/src/github.com/atw527/image-match/data/frames/".format(video_id))

# cleaning up
print "Cleaning up...", video_id
if video_id != "":
    os.system("rm -f frames/" + video_id + "/*.jpg")
    os.system("rmdir " + video_id)
    os.system("rm -f video/" + video_id + "*")

print "Done!", video_id

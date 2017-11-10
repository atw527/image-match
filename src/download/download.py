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
from functools import partial
from random import randint

def signal_handler(video_id, x, conn, signal, frame):
        print('Shuting down...')

        # put the item we were working on back in the queue for someone else to pick up
        query = "UPDATE download SET host = null, container = null, started = null WHERE video_id = '" + video_id + "' LIMIT 1"
        x.execute(query)

        # delete any progress we made on the task
        if video_id != "":
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
    sql = "SELECT video_id FROM download WHERE host IS NULL LIMIT 1"
    x.execute(sql)
    if x.rowcount == 1:
        break

row = x.fetchone()
video_id = row[0]

query = "UPDATE download SET host = %s, container = %s, started = %s WHERE video_id = %s LIMIT 1"
args = (hostname, container, time.strftime('%Y-%m-%d %H:%M:%S'), video_id)
x.execute(query, args)

print "[{0}] Picking up task.".format(video_id)

# now is when we care if the script is killed
signal.signal(signal.SIGINT, partial(signal_handler, video_id, x, conn))
signal.signal(signal.SIGTERM, partial(signal_handler, video_id, x, conn))

# download
# 160  mp4  256x144    DASH video
# 133  mp4  426x240    DASH video
# 134  mp4  640x360    DASH video
# 135  mp4  854x480    DASH video
# 136  mp4  1280x720   DASH video
# 137  mp4  1920x1080  DASH video
print "video/{0}.mp4".format(video_id)
if os.path.isfile("video/{0}.mp4".format(video_id)):
    print "[{0}] Video exists in the filesystem; skipping.".format(video_id)

    query = "UPDATE download SET completed = %s WHERE video_id = %s LIMIT 1"
    args = (time.strftime('%Y-%m-%d %H:%M:%S'), video_id)
    x.execute(query, args)
else:
    print "[{0}] Downloading...".format(video_id)
    dl_command = "youtube-dl --write-thumbnail --write-description --write-info-json --restrict-filenames -o 'video/%(id)s.%(ext)s' -f {0} https://www.youtube.com/watch?v={1} >/tmp/stdout-{1} 2>/tmp/stderr-{1}"
    (return_val, output) = commands.getstatusoutput(dl_command.format("137", video_id)) # try 1080p first

    if return_val == 1:
        print "[{0}] Attempting 720p...".format(video_id)
        (return_val, output) = commands.getstatusoutput(dl_command.format("136", video_id)) # fallback to 720p

    stdout = open("/tmp/stdout-" + video_id).read()
    stderr = open("/tmp/stderr-" + video_id).read()

    query = "UPDATE download SET completed = %s, exit_code = %s, stdout = %s, stderr = %s WHERE video_id = %s LIMIT 1"
    args = (time.strftime('%Y-%m-%d %H:%M:%S'), return_val, stdout, stderr, video_id)
    x.execute(query, args)

    # queue it up for processing
    query = "INSERT IGNORE INTO render (video_id) VALUES ({0})".format(video_id)
    x.execute(query)

print "[{0}] Done!".format(video_id)

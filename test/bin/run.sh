#!/bin/bash

if [ ! -f /usr/local/bin/youtube-dl ]; then
    apt-get update
    apt-get install -y curl ffmpeg python
    curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
fi

chmod a+rx /usr/local/bin/youtube-dl

youtube-dl --write-thumbnail --write-description --write-info-json --restrict-filenames \
    -o '/usr/test/%(upload_date)s_%(id)s.%(ext)s' -f 137 \
    -a /usr/local/bin/queue.txt

mkdir /usr/test/l-_NYHkKdwQ

#ffmpeg -i /usr/test/20170817_l-_NYHkKdwQ.mp4 -r 15/1 -f image2 /usr/test/l-_NYHkKdwQ/l-_NYHkKdwQ.%6d.jpg

#!/bin/bash

if [ ! -f /usr/local/bin/youtube-dl ]; then
    apt-get update
    apt-get install -y curl ffmpeg python
    curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
fi

chmod a+rx /usr/local/bin/youtube-dl

youtube-dl --write-thumbnail --write-description --write-info-json --restrict-filenames \
    -o '/usr/test/%(id)s.%(ext)s' -f 137 \
    -a /usr/local/bin/queue.txt

mkdir /usr/test/l-_NYHkKdwQ
ffmpeg -i /usr/test/l-_NYHkKdwQ.mp4 -r 10/1 -f image2 /usr/test/l-_NYHkKdwQ/%6d.jpg

mkdir /usr/test/_-0XprLfiNQ
ffmpeg -i /usr/test/_-0XprLfiNQ.mp4 -r 10/1 -f image2 /usr/test/_-0XprLfiNQ/%6d.jpg

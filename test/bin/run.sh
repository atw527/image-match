#!/bin/bash

if [ ! -f /usr/local/bin/youtube-dl ]; then
    apt-get update
    apt-get install -y curl ffmpeg python
    curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
fi

chmod a+rx /usr/local/bin/youtube-dl

youtube-dl --write-thumbnail --write-description --write-info-json --restrict-filenames \
    -o '/usr/test/%(upload_date)s_%(id)s.%(ext)s' -f 'bestvideo[height<=1080]+bestaudio/best[height<=1080]' \
    -a /usr/local/bin/queue.txt

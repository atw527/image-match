#!/bin/bash

if [ ! -f /usr/local/bin/youtube-dl ]; then
    apt-get update
    apt-get install -y curl ffmpeg
    curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
fi

chmod a+rx /usr/local/bin/youtube-dl

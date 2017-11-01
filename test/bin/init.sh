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

cd /usr/test/
for f in *.mp4
do
    dir="${f%.*}"
	if [ ! -d $dir ]; then
        echo $dir not found
        mkdir /usr/test/$dir
        ffmpeg -i /usr/test/$f -r 10/1 -f image2 /usr/test/$dir/%6d.jpg
    else
        echo $dir exists
    fi
done

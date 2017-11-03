#!/bin/bash

#apt-get update
#apt-get install -y curl ffmpeg python

#curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
#chmod a+rx /usr/local/bin/youtube-dl

#youtube-dl --write-thumbnail --write-description --write-info-json --restrict-filenames \
#    -o '/usr/local/video/%(id)s.%(ext)s' -f 137 \
#    -a /usr/local/bin/queue.txt

cd /usr/local/video/
for f in *.mp4
do
    dir="${f%.*}"
	if [ ! -d "$dir" ]; then
        echo $dir not found
        mkdir /usr/local/frames/$dir
        ffmpeg -i /usr/local/video/$f -r 10/1 -f image2 /usr/local/frames/$dir/%6d.jpg
    else
        echo $dir exists
    fi
done

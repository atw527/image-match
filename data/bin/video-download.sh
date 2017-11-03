#!/bin/bash

# download mp4s and related meta
youtube-dl --write-thumbnail --write-description --write-info-json --restrict-filenames \
    -o '/usr/local/video/%(id)s.%(ext)s' -f 137 \
    -a /usr/local/bin/queue.txt

# blow up the filesystem with thousands of JPGs (extract video files for image comparison)
cd /usr/local/video/
for f in *.mp4
do
    dir="${f%.*}"
	if [ ! -d "$dir" ]; then
        echo $dir not found; creating and building frames...
        mkdir /usr/local/frames/$dir
        ffmpeg -i /usr/local/video/$f -r 10/1 -f image2 /usr/local/frames/$dir/%6d.jpg > /dev/null
        echo $dir frame build complete!
    else
        echo $dir exists
    fi
done

# report to Front which videos we can process
#TODO

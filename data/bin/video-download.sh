#!/bin/bash

# download mp4s and related meta
if [ -f /usr/local/bin/queue.txt ]; then
    echo queue file found, starting download

    youtube-dl --write-thumbnail --write-description --write-info-json --restrict-filenames \
        -o '/usr/local/video/%(id)s.%(ext)s' -f 137 \
        -a /usr/local/bin/queue.txt
else
    echo queue file NOT found, skipping download
fi

# blow up the filesystem with thousands of JPGs (extract video files for image comparison)
cd /usr/local/video/
for f in *.mp4
do
    dir="${f%.*}"
	if [ ! -d "/usr/local/frames/$dir" ]; then
        echo $dir not found, creating and building frames...
        mkdir /usr/local/frames/$dir
        ffmpeg -i /usr/local/video/$f -r 10/1 -f image2 /usr/local/frames/$dir/%6d.jpg > /dev/null
        echo $dir frame build complete!
        echo $dir filter out duplicate frames...
        /usr/local/bin/frame-dedup.php "/usr/local/frames/$dir"
        echo $dir filter complete!
    else
        echo $dir exists
    fi
done

echo MlyNV-fDy10 filter out duplicate frames...
/usr/local/bin/frame-dedup.php "/usr/local/frames/MlyNV-fDy10"
echo MlyNV-fDy10 filter complete!

# fix some permissions
chmod -R +r /usr/local/video
chmod -R +r /usr/local/frames

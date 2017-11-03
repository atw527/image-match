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
    else
        echo $dir exists
    fi
done

# report to Front which videos we can process
#TODO (basically some rsync commands of the meta files)
/usr/local/bin/ssh-test.exp andrew a01-docker-01

if [ ! $? -eq 0 ]
then
    rsync data/video/*.json andrew@a01-docker-01:/home/andrew/go/src/github.com/image-match/data/video/
    rsync data/video/*.description andrew@a01-docker-01:/home/andrew/go/src/github.com/image-match/data/video/
    rsync data/video/*.jpg andrew@a01-docker-01:/home/andrew/go/src/github.com/image-match/data/video/
else
    echo "SSH test failed, can't reach Front.  Make sure the host exist and has out key."
fi

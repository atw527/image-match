#!/bin/bash

cd "${0%/*}"
cd ..
cd video

for f in *.mp4
do
    dir="${f%.*}"
	if [ -d "../frames/$dir" ]; then
        uptime
        echo $dir filter out duplicate frames...
        ../bin/duplicates.php "../frames/$dir"
        echo $dir filter complete!
    else
        echo "$dir does not exist for some reason"
    fi
done

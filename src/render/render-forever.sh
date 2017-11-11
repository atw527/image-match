#!/bin/bash

cd "${0%/*}"

chmod -R a+r /usr/local/data

while [ true ]; do
        python /usr/local/bin/render.py
        echo `date` - program ended or connection lost - retrying in 5 seconds...
        sleep 5
done

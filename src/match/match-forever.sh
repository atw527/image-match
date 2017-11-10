#!/bin/bash

cd "${0%/*}"

while [ true ]; do
        python /usr/local/bin/match.py
        echo `date` - program ended or connection lost - retrying in 5 seconds...
        sleep 5
done

#!/bin/bash

cd "${0%/*}"

while [ true ]; do
        python ./match.py
        echo `date` - respawning in 5 seconds...
        sleep 5
done

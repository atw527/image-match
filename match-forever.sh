#!/bin/bash

cd "${0%/*}"

while [ true ]; do
        python ./match.py
        sleep 5
done

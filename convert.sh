#!/bin/bash

if [ -z "$1" ]
then
    echo "Specify input glob"
    exit 1
fi
if [ -z "$2" ]
then
    echo "Specify output file"
    exit 1
fi

ffmpeg -r 5 -pattern_type glob -i "$1" -c:v libx264 $2

#!/bin/bash

ffmpeg -r 5 -pattern_type glob -i 'camera/*.jpg' -c:v libx264 output/video-file.mp4

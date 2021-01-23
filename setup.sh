#!/bin/bash

sudo apt install -y ffmpeg python3-venv

python3 -m venv .venv
source env/bin/activate

pip3 install -r requirements.txt

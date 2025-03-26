#!/bin/bash
default_sink=$(pactl info | grep -P -o "(?<=Default Sink: ).*")
dev_name=${default_sink##*.}
if [[ $dev_name = "analog-stereo" ]]; then
    dev_name="Line Out"
elif [[ $dev_name = "hdmi-stereo" ]]; then
    dev_name="Speakers"
fi
echo DEVNAME=$dev_name
#!/bin/bash
# script to cycle audio outputs

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

setdevice () {
    pactl set-default-sink $1
    dev_name=${1##*.}
    if [[ $dev_name = "analog-stereo" ]]; then
        dev_name="Line Out"
    elif [[ $dev_name = "hdmi-stereo" ]]; then
        dev_name="Speakers"
    fi

    echo DEVNAME=$dev_name

    id=$($SCRIPT_DIR/notify-send/notify-send.sh \
        --replace-file=/tmp/audiooutputswitcher \
        --print-id \
        "Audio Output Switched" \
        "New Audio Output is '$dev_name'")
    
    sleep 0.25
    ( speaker-test -t sine -f 220 )& pid=$! ; sleep 0.1s ; kill -9 $pid
    sleep 1.75
    $SCRIPT_DIR/notify-send/notify-send.sh --close=$id
    # timeout 0.5 play /usr/share/sounds/gnome/default/alerts/drip.ogg -q 2> /dev/null
    exit
}

# start the icon program
[[ -z $(ps -fA | grep  "python.*cycleaudio.py" | grep -v 'grep') ]] && python3 $SCRIPT_DIR/cycleaudio.py &

default_sink=$(pactl info | grep -P -o "(?<=Default Sink: ).*")

unset first
unset next_line
while read -r num device status ; do
    [[ $next_line == "t" ]] && setdevice $device
    [[ $device == $default_sink ]] && next_line="t"
    [[ -z ${first+.} ]] && first=$device
done < <(pactl list sinks short | awk -F '\t' '{print $1,$2,$5}')

[[ $next_line == "t" ]] && setdevice $first

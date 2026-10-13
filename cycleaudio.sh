#!/bin/bash
# script to cycle audio outputs

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

setdevice () {
    pactl set-default-sink $1
    echo DEVNAME=$1
    jingle &

    # trim list sinks down to the current sink and whatever after it, just have
    # to use -m 1 to grab from the right section
    device_info=$(
        pactl list sinks |
        grep "$1" -m 1 -A 500)

    product_name=$(
        grep -oP "(?<=device.product.name = \").+(?=\")" -m 1 <<< "$device_info")

    if [[ -z $product_name ]] then
        product_name=$(
            grep -oP "(?<=device.description = \").+(?=\")" -m 1 <<< "$device_info")
    fi

    mapping=$(cat $SCRIPT_DIR/dev2name.txt  | grep "^$1|")
    if [[ -n $mapping ]] then
        nice_name=$(cut -d "|" -f 2 <<< "$mapping")
    else
        nice_name=${1##*.}
    fi


    id=$($SCRIPT_DIR/notify-send/notify-send.sh \
        --replace-file=/tmp/audiooutputswitcher \
        --print-id \
        --app-name "Cycle Audio" \
        -f -t 2250 \
        "Audio Output Switched: $nice_name" \
        "New Audio Output is $product_name")
    
    exit
}

jingle () {
    sleep 0.2
    speaker-test -t sine -f 220 -S 30 > /dev/null &
    pid=$!
    sleep 0.1s
    kill -9 $pid
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

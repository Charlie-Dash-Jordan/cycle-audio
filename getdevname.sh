#!/bin/bash
default_sink=$(pactl info | grep -P -o "(?<=Default Sink: ).*")
echo "$default_sink"

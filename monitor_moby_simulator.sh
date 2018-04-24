#!/bin/bash

monitoring_filename=$1

while sleep 5m
do
    for pid in `pgrep -f moby_simulator.py`
    do
        echo `ps -p $pid -o %cpu,%mem,cmd`
    done
done

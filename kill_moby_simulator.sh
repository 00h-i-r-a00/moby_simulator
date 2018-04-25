#!/bin/bash

monitoring_filename=$1
finish=0
while sleep 1s
do
    for pid in `pgrep -f moby_simulator.py`
    do
        echo "Killing process: "
        echo '$pid'
        `kill -9 $pid`
    done

    for pid in `pgrep -f generate_messages.py`
    do
        echo "Killing process: "
        echo `$pid`
        `kill -9 $pid`
    done
    let "finish++"
    if [ $finish == 600 ]; then
        echo "Killed all moby_simulator.py and generate_messages.py processes found in 10 minutes"
        break
    fi
done

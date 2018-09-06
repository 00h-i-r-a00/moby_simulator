#!/bin/bash

#meant to use as a script for a cronjob

while sleep 5s; do

    onegig=$(echo "scale=4; 1024 * 1024" | bc -l)
    total_mem_cons=`vmstat -n -s | grep "used memory" | awk '{print $1}'`
    tot_mem=`vmstat -n -s | grep "total memory" | awk '{print $1}'`
    total_mem_cons=$(echo "scale=4; $total_mem_cons / $onegig" | bc -l)
    tot_mem=$(echo "scale=4; $tot_mem / $onegig" | bc -l)
    difference=`bc <<< "scale = 4; $tot_mem - $total_mem_cons"`

    limit=30

    #If all simulations consume more than the $limit space, then kill them and log

    if (( $(echo "$difference < $limit" | bc -l) )); then
        for pid in `pgrep -f moby_simulator.py`; do
            configuration=`ps aux | grep $pid | head -n 1 | awk '{for(i=12;i<=NF;++i)print $i}' | head -3 | tail -1`
            kill -9 $pid
            echo "KILLED:::$(date):::$configuration"
        done
        #to ensure that run_simulations.py and generate_messages.py get killed as well
        #note: above loop is to have track of the configurations that get killed
        killall python

    fi

done
#TODO: add this script to the launching script
#TODO: kill the previous version in the launching script

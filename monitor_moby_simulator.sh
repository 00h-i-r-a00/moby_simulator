#!/bin/bash

monitoring_filename=$1

while sleep 5m
do
    sum_mem=0
    sum_cpu=0
    sum_proc=0

##Computing Cumulative CPU and Memory Consumption for moby_simulator.py    
    for pid in `pgrep -f moby_simulator.py`
    do
        x=`ps -p $pid -o %cpu,%mem,cmd`
        mem=`echo $x | cut -d " " -f 5`
        cpu=`echo $x | cut -d " " -f 4`
        sum_mem=`echo "$mem + $sum_mem" | bc -l`
        sum_cpu=`echo "$cpu + $sum_cpu" | bc -l`
        let "sum_proc++"
         
    done

    sum_mem2=0
    sum_cpu2=0
    sum_proc2=0

###Computing Cumulative CPU and Memory Consumption for generate_messages.py###
    for pid in `pgrep -f generate_messages.py`
    do  
        x=`ps -p $pid -o %cpu,%mem,cmd`
        mem=`echo $x | cut -d " " -f 5`
        cpu=`echo $x | cut -d " " -f 4`
        sum_mem2=`echo "$mem + $sum_mem2" | bc -l`
        sum_cpu2=`echo "$cpu + $sum_cpu2" | bc -l`
        let "sum_proc2++"
        
    done    

    if [[ $sum_proc -ne 0 ]]; then
        avg_cpu=`echo "$sum_cpu / $sum_proc" | bc -l`
    
    else 
        
        avg_cpu="No Process Running"
    fi

    if [[ $sum_proc2 -ne 0 ]]; then
        avg_cpu2=`echo "$sum_cpu2 / $sum_proc2" | bc -l`
    
    else 
        
        avg_cpu2="No Process Running"
    fi
    

   
    timestamp=`date`
    echo "--------------------------------------------"
    echo "Statistics for Last 5min"
    echo "Timestamp: $timestamp"
    echo "Aggregated Memory for moby_simulator.py: $sum_mem"
    echo "Average CPU for moby_simulator.py: $avg_cpu"
    echo "Aggregated Memory for generate_messages.py: $sum_mem2"
    echo "Average CPU for generate_messages.py: $avg_cpu2"

done

#!/bin/bash

queuesizes=('900' '1000' '1100')
#message_generation_types=(1 2)
#for i in "${message_generation_types[@]}"
#do
#tmux new-session -d -s "messagegeneration_"$i" 'python generate_messages.py --messagegenerationtype "$i"'"
#done

##sleep time##

#for i in 0 1 2 3
#do
#    echo "Sleeping 1 minute .."
#    sleep $i'm'
#done

configurations=(0 1)
deliveryratiotypes=(1 2)

for config in "${configurations[@]}"
do
    for delratio in "${deliveryratiotypes[@]}"
    do
        for queuesize in "${queuesizes[@]}"
        do
            tmux_session_name='queuesize_'$queuesize'_configuration_'$config'_deliveryratiotype_'$delratio
            outputfolder=$results_folder_prefix'_queuesize_'$queuesize'_configuration_'$config'_deliveryratiotype_'$delratio
            python_cmd='python moby_simulator.py --deliveryratiotype '$delratio' --configuration '$config' --usequeue --queuesize '$queuesize' --outputfoldername '$outputfolder
            echo tmux new-session -d -s $tmux_session_name" '"$python_cmd"'"

        done
    done
done

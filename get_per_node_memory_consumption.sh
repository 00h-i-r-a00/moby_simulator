#!/bin/sh

#run as ./get_per_node_memory_consumption.sh node1 node2 node3 | grep STATUS
#put above in a while loop to do continous monitoring; for example ==> while true; do ./get_per_node_memory_consumption.sh achtung02 achtung03 | grep STATUS; sleep 2; done >> log.log
#doing above will continuously monitor for memory as well as kill processes if the memory space on achtung reaches a certain limit while adding it all in a log which can be monitored with something like tail -f log.log

for server in "$@"; do
    ssh $server << 'EOF'
    num_proc=0
    sum_virt=0

    procs=""
    procs=`pgrep -f moby_simulator.py`
    if [[ "$procs" ]]; then
		for pid in `pgrep -f moby_simulator.py`; do
			echo "PID: $pid"
		    x=`ps -p "$pid" -o %cpu,%mem,cmd,vsize`
            virt=`echo $x | cut -d " " -f 9`
            sum_virt=`echo "$virt + $sum_virt" | bc -l`
			let "num_proc++"
        done

        onegig=$(echo "scale=4; 1024 * 1024" | bc -l)
        echo "STATUS: Number of moby_simulator.py processes on node $HOSTNAME: $num_proc"
        echo "STATUS: Total Memory Consumption by moby_simulator.py on node $HOSTNAME: $(echo "scale=4; $sum_virt / $onegig" | bc -l) Gb"
        total_mem_cons=`vmstat -n -s | grep "used memory" | awk '{print $1}'`
        tot_mem=`vmstat -n -s | grep "total memory" | awk '{print $1}'`
        total_mem_cons=$(echo "scale=4; $total_mem_cons / $onegig" | bc -l)
        tot_mem=$(echo "scale=4; $tot_mem / $onegig" | bc -l)
        difference=`bc <<< "scale = 4; $tot_mem - $total_mem_cons"`
        echo "STATUS: Total Used Memory On node $HOSTNAME: $total_mem_cons Gb"
        echo "STATUS: Total Memory on node $HOSTNAME: $tot_mem Gb"

        limit=15

        #If all simulations consume more than the $limit space, then kill them and log

        if (( $(echo "$difference < $limit" | bc -l) )); then
            echo "STATUS: ALERT ::: Only $limit Gb left on node $server ::: killing all moby processes"
            for pid in `pgrep -f moby_simulator.py`; do
                configuration=`ps aux | grep $pid | head -n 1 | awk '{for(i=12;i<=NF;++i)print $i}' | head -3 | tail -1`
                kill -9 $pid
                echo "STATUS: Killed Configuration: $configuration"
            done

        fi

    else
		echo "STATUS: No moby_simulator.sh process running on node $HOSTNAME"

    fi
EOF
done

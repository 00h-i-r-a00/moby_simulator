#!/bin/sh

#run as ./get_per_node_memory_consumption.sh node1 node2 node3 | grep STATUS

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

        echo "STATUS: Number of moby_simulator.py processes on node $HOSTNAME: $num_proc"
        sum_virt=`echo "sum_virt / 1000000" | bc -l`
        echo "STATUS: Total Memory Consumption by moby_simulator.py on node $HOSTNAME: $sum_virt Gb"
        total_mem_cons=`vmstat -n -s | grep "used memory" | awk '{print $1}'`
        tot_mem=`vmstat -n -s | grep "total memory" | awk '{print $1}'`
        echo "STATUS: Total Used Memory On node $HOSTNAME: $total_mem_cons Kb"
        echo "STATUS: Total Memory on node $HOSTNAME: $tot_mem Kb"

        difference=`echo "$total_mem - $total_mem_cons" | bc -l`

        if [[ "$difference" -lt 20000000 ]]; then
            echo "STATUS: ALERT ::: Only 20G left on node $server"
        fi

    else
		echo "STATUS: No moby_simulator.sh process running on node $HOSTNAME"

    fi
EOF
done

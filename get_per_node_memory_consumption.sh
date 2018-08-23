#!/bin/sh
for server in achtung02 achtung03 achtung04 achtung05 achtung06 achtung07 achtung10 achtung11 achtung12 achtung13 achtung14 achtung15  achtung16 achtung17; do
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
        
        echo "Number of moby_simulator.py processes on node $server: $num_proc"
        sum_virt=`echo "sum_virt / 1000000" | bc -l`
        echo "Total Memory Consumption by moby_simulator.py on node $server: $sum_virt Gb"        
        total_mem_cons=`vmstat -n -s | grep "used memory" | awk '{print $1}'`
        tot_mem=`vmstat -n -s | grep "total memory" | awk '{print $1}'`
        echo "Total Memory Consumption on node $server: $total_mem_cons"
        echo "Total memory on node $server: $tot_mem"
                
    else
		echo "No monitor_moby_simulator.sh process running on node $server"
        
    fi
EOF
done

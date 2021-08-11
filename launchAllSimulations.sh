#!/bin/sh
for server in achtung02 achtung03 achtung04 achtung05 achtung06 achtung07 achtung08 achtung09 achtung11 achtung12 achtung13 achtung14 achtung15  achtung16 achtung17; do
    ssh $server << EOF
    echo "######################################################" $SHELL
    hostname
    pkill -f monitor_moby_simulator.sh
    cd moby/moby_simulator
    nohup ./run_simulations.py > data/logs/$server.nohup 2>&1 &!
EOF
done

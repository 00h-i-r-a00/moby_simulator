#!/bin/sh
for server in achtung02 achtung03 achtung04 achtung05 achtung06 achtung07 achtung10 achtung11 achtung12 achtung13 achtung14 achtung15  achtung16 achtung17; do
    ssh $server << EOF
    killall python
    killall java
    killall python3
EOF
done

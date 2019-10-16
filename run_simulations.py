#!/usr/bin/env python3
import getpass
import json
import os
import socket
import subprocess
import time
import math
import pdb

SLEEP_TIME = 1 * 60

RESULTS_DIR = "data/results/"
RESULTS_EXT = ".csv"
MESSAGE_DELAYS_EXT = '.md'
QUEUE_OCCUPANCY_EXT = '.qo'

def get_total_concurrent_processes():
    return 1
    proc_meminfo_output = subprocess.check_output('cat /proc/meminfo', shell=True)
    total_mem = float(subprocess.check_output("vmstat -n -s | grep 'total memory' | awk '{print $1}'", shell=True))
    used_mem = subprocess.check_output("vmstat -n -s | grep 'used memory' | awk '{print $1}'", shell=True)
    free_mem = int(total_mem) - int(used_mem)
    avg_mem_consumption_per_process = 35 * 1024 * 1024
    total_concurrent_processes = int(math.floor(free_mem/avg_mem_consumption_per_process))
    max_total_concurrent_processes = int(math.floor(total_mem/(avg_mem_consumption_per_process * 2)))
    return min(total_concurrent_processes, max_total_concurrent_processes)

def main():
    #get current hostname
    me = getpass.getuser()
    killswitch = "/home/" + me + '/killswitch'
    hostname = socket.gethostname()
    print (hostname)
    results_stripped = []
    with open (hostname+".json") as conf_file:
        confs = json.load(conf_file)
    for conf in confs:
        # Check if the results exist, if they do, skip to the next one!
        run = False
        cnf_id = str(conf["configuration"])
        results = [RESULTS_DIR + cnf_id + i for i in [RESULTS_EXT, MESSAGE_DELAYS_EXT, QUEUE_OCCUPANCY_EXT]]
        for result_file in results:
            if not os.path.exists(result_file):
                run = True
        if run:
            results_stripped.append(conf)
        else:
            print("Skipping config:", cnf_id)
    confs = results_stripped
    conf_pointer = 0
    while conf_pointer < len(confs):
        if(os.path.isfile(killswitch)):
            print("Killswitch encountered!!")
            subprocess.check_output("killall python3 -u " + me, shell=True)
            return
        number_of_moby_processes_cmd = 'ps aux | grep `whoami` | grep moby_simulator.py | wc -l'
        running_moby_processes = int(subprocess.check_output(number_of_moby_processes_cmd, shell=True)) - 1 # Discount grep process.
        number_of_generate_messages_cmd = 'ps aux | grep `whoami` | grep generate_messages.py | wc -l'
        running_moby_processes += int(subprocess.check_output(number_of_generate_messages_cmd, shell=True)) - 1 # Discount grep process.
        running_moby_processes -= 2
        TOTAL_CONCURRENT_PROCESSES = get_total_concurrent_processes()
        processes_to_schedule = max(TOTAL_CONCURRENT_PROCESSES - running_moby_processes, 0)
        print("Running moby", running_moby_processes, "To schedule", processes_to_schedule)
        new_pointer = conf_pointer + processes_to_schedule
        if new_pointer > len(confs):
            new_pointer = len(confs)
        confs_subset = confs[conf_pointer:new_pointer]
        conf_pointer = new_pointer
        for conf in confs_subset:
            msg_gen_string = 'nohup sh -c "./generate_messages.py '
            for key, value in conf.items():
                msg_gen_string += "--" + key + " " + str(value) + " "
            cnf_id = str(conf["configuration"])
            print(conf)
            msg_gen_string += ' && java -Xmx180g -XX:+UseParallelGC -XX:-UseGCOverheadLimit -cp bin/:jars/*:  MobySimulator ' + cnf_id + '" > data/logs/' + cnf_id + '.nohup &'
            print (msg_gen_string)
            os.system(msg_gen_string)
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    main()

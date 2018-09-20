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

def get_total_concurrent_processes():
    proc_meminfo_output = subprocess.check_output('cat /proc/meminfo', shell=True)
    total_mem = float(subprocess.check_output("vmstat -n -s | grep 'total memory' | awk '{print $1}'", shell=True))
    used_mem = subprocess.check_output("vmstat -n -s | grep 'used memory' | awk '{print $1}'", shell=True)
    free_mem = int(total_mem) - int(used_mem)
    avg_mem_consumption_per_process = 20 * 1024 * 1024
    total_concurrent_processes = int(math.floor(free_mem/avg_mem_consumption_per_process))
    max_total_concurrent_processes = int(math.floor(total_mem/(avg_mem_consumption_per_process * 2)))
    return min(total_concurrent_processes, max_total_concurrent_processes)

def main():
    #get current hostname
    me = getpass.getuser()
    killswitch = "/home/" + me + '/killswitch'
    hostname = socket.gethostname()
    print (hostname)
    with open (hostname+".json") as conf_file:
        confs = json.load(conf_file)
    conf_pointer = 0
    while conf_pointer < len(confs):
        if(os.path.isfile(killswitch)):
            print("Killswitch encountered!!")
            subprocess.check_output("killall python3 -u " + me, shell=True)
            return
        number_of_moby_processes_cmd = 'pgrep -u `whoami` -f moby_simulator.py'
        running_moby_processes = len(subprocess.check_output(number_of_moby_processes_cmd, shell=True).split())
        TOTAL_CONCURRENT_PROCESSES = get_total_concurrent_processes()
        processes_to_schedule = TOTAL_CONCURRENT_PROCESSES - running_moby_processes
        if processes_to_schedule == 0:
            continue
        new_pointer = conf_pointer + processes_to_schedule
        if new_pointer > len(confs):
            new_pointer = len(confs)
        confs_subset = confs[conf_pointer:new_pointer]
        conf_pointer = new_pointer
        for conf in confs_subset:
            msg_gen_string = "./generate_messages.py "
            for key, value in conf.items():
                msg_gen_string += "--" + key + " " + str(value) + " "
            print (msg_gen_string)
            os.system(msg_gen_string)
            print (conf)
            cnf_id = str(conf["configuration"])
            os.system("nohup ./moby_simulator.py --configuration " + cnf_id + " > data/logs/"+ cnf_id+".nohup" +"&")
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    main()

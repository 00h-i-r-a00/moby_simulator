#!/usr/bin/env python3
import json
import os
import socket
import subprocess
import time

TOTAL_CONCURRENT_PROCESSES = 10
SLEEP_TIME = 1 * 60

def main():
    hostname = socket.gethostname()
    print hostname
    with open (hostname+".json") as configs:
        confs = configs.readline().strip().split("!")
        confs = confs[1:]
    conf_pointer = 0
    while conf_pointer < len(confs):
        numer_of_moby_processes_cmd = 'ps aux | grep "python3 moby_simulator.py" | wc -l'
        process = subprocess.Popen(numer_of_moby_processes_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        running_moby_processes = int(out.decode())
        running_moby_processes -= 1 # Remove the grep process counted.
        processes_to_schedule = TOTAL_CONCURRENT_PROCESSES - running_moby_processes
        new_pointer = conf_pointer + processes_to_schedule + 1
        confs_subset = confs[conf_pointer:new_pointer]
        conf_pointer = new_pointer
        for conf in confs_subset:
            cnf = json.loads(conf)
            msg_gen_string = "./generate_messages.py "
            for key, value in cnf.iteritems():
                 msg_gen_string += "--" + key + " " + str(value) + " "
            print msg_gen_string
            os.system(msg_gen_string)
            print cnf
            cnf_id = str(cnf["configuration"])
            os.system("nohup ./moby_simulator.py --configuration " + cnf_id + " > data/logs/"+ cnf_id+".nohup" +"&")
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import itertools
import os
import os.path
import pdb
from datetime import datetime as dt
import subprocess
from collections import defaultdict

###create a directory to store all the configs######
if not os.path.exists(os.getcwd() + '/data/configs'):
    os.makedirs(os.getcwd() + '/data/configs')
else:
    #remove already existing configs
    files = os.listdir(os.getcwd() + '/data/configs')
    for f in files:
        os.remove(os.getcwd() + '/data/configs/' + f)
####################################################

achtungs = []
achtungs200 = ["achtung02", "achtung03", "achtung04", "achtung05", "achtung06", "achtung07", "achtung12", "achtung13", "achtung14", "achtung15", "achtung16"]
achtungs100 = ["achtung10", "achtung11"]
# "achtung17"]
# achtungs50  = ["achtung08", "achtung09"]
for i in range(0, 3):
    achtungs.extend(achtungs200)
for i in range(0, 2):
    achtungs.extend(achtungs100)
# achtungs.extend(achtungs50)
achtungpool = itertools.cycle(achtungs)

# Makes keeping track of different runs easier than manually changing this counter.
#YYYYMMDDHHMMSS
run_number = dt.now().strftime("%Y%m%d%H%M%S")
start_days = [53]
number_of_days = [3, 4, 5]
cities = [0]
cooldowns = [24]
number_of_messages = [30000]
#queuesizes = [queuesize for queuesize in xrange(0,max_queue_size + 1,10)]
queuesizes = [0]
seeds = [373523167]
distributiontype = ['region_sms_based']
ttls = [73]
#distributiontype = ['region_sms_based']
thresholds = [0, 2, 4, 6, 8, 10, 12]
#infinite since we are intially taking an estimate of the possible PDRs
max_number = 10 #max number of dos messages to send
dos_numbers = [0]
# (% towers to jam, jamming logic)
jamtower = [(0, 0)] # Different jamming scenarios.
slack_hook = ""

def main():
    config = {}
    achtung_dict = defaultdict(list)
    config_ctr = 0
    print("Cleaning current config files and writing new ones.")
    for f in achtungs:
        if os.path.isfile(os.getcwd() + '/' + f + '.json'):
            os.remove(f+".json")

    for val_seed in seeds:
        for val_ttl in ttls:
            for val_start in start_days:
                for val_nod in number_of_days:
                    for val_city in cities:
                        for val_cd in cooldowns:
                            for val_nm in number_of_messages:
                                for val_queue in queuesizes:
                                    for val_disttype in distributiontype:
                                        for val_threshold in thresholds:
                                            for val_dosnumber in dos_numbers:
                                                for val_jamtower in jamtower:
                                                    current_achtung = next(achtungpool)
                                                    config["start-day"] = val_start
                                                    config["end-day"] = val_start+val_nod
                                                    config["ttl"] = val_nod * 24
                                                    config["city-number"] = val_city
                                                    config["cooldown"] = val_cd
                                                    config["number"] = val_nm
                                                    config["queuesize"] = val_queue
                                                    config["seed"] = val_seed
                                                    config["distributiontype"] = val_disttype
                                                    config["configuration"] = str(run_number) + "_" + str(config_ctr)
                                                    config["threshold"] = val_threshold
                                                    config["dos-number"] = val_dosnumber
                                                    config["jam-tower"] = val_jamtower[0]
                                                    config["jam-tower-logic"] = val_jamtower[1]
                                                    config["slack-hook"] = slack_hook
                                                    config_ctr += 1
                                                    achtung_dict[current_achtung].append(config)
                                                    #keeping track of the parameters used inside configurations to help with graphs
                                                    with open('data/configs/' + config["configuration"] + '.txt', 'w') as out:
                                                        json.dump(config, out)
                                                    config = {}
    for current_achtung in achtung_dict.keys():
        with open(current_achtung+".json", 'w') as outfile:
            json.dump(achtung_dict[current_achtung], outfile)
    print("Uploading configs.", config_ctr)
    os.system("scp achtung*.json achtung:moby_simulator/")

    print("Uploading config contents")
    os.system("scp -r data/configs/ achtung:moby_simulator/data/ ")

if __name__ == "__main__":
    main()

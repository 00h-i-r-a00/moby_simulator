#!/usr/bin/env python3
import json
import itertools
import os
import os.path
import pdb
from datetime import datetime as dt
import subprocess
from collections import defaultdict
from itertools import product

achtungs = []
achtungs200 = ["achtung02", "achtung03", "achtung04", "achtung05", "achtung06", "achtung07", "achtung12", "achtung13", "achtung14", "achtung15", "achtung16"]
achtungs100 = ["achtung10", "achtung11"]
for i in range(0, 3):
    achtungs.extend(achtungs200)
for i in range(0, 2):
    achtungs.extend(achtungs100)
achtungpool = itertools.cycle(achtungs)

# Makes keeping track of different runs easier than manually changing this counter.
#YYYYMMDDHHMMSS
run_number = dt.now().strftime("%Y%m%d%H%M%S")
start_days = [53]
number_of_days = [3, 4, 5]
cities = [0]
cooldowns = [24]
number_of_messages = [30000]
queuesizes = [0]
seeds = [373523167]
distributiontype = ['region_sms_based']
ttls = [73]
thresholds = [0, 2, 4, 6, 8, 10, 12]
#infinite since we are intially taking an estimate of the possible PDRs
max_number = 10 #max number of dos messages to send
dos_numbers = [0]
# (% towers to jam, jamming logic)
jamtower = [(0, 0)] # Different jamming scenarios.
contact_lists = ["0hop1thresh"]
trust_simulation = True
trust_scores = ["2hop1thresh", "1hop1thresh"]
slack_hook = ""

CONFIG_FILE = "config.json"

def main():
    config = {}
    achtung_dict = defaultdict(list)
    config_ctr = 0
    print("Cleaning current config files and writing new ones.")
    for f in achtungs:
        if os.path.isfile(os.getcwd() + '/' + f + '.json'):
            os.remove(f + ".json")

    global trust_scores
    if not trust_simulation:
        trust_scores = [""]

    for val_seed, val_ttl, val_start, val_nod, val_city, val_cd, val_nm, \
            val_queue, val_disttype, val_threshold, val_dosnumber, \
            val_jamtower, val_cl, val_ts in product(
            seeds, ttls, start_days, number_of_days, cities,
            cooldowns, number_of_messages, queuesizes, distributiontype,
            thresholds, dos_numbers, jamtower, contact_lists, trust_scores):
        current_achtung = next(achtungpool)
        config["start-day"] = val_start
        config["end-day"] = val_start+val_nod
        config["ttl"] = val_nod * 24
        config["city-number"] = val_city
        config["cooldown"] = val_cd
        # Scale number of days according to simulation length
        config["number"] = int(val_nm * (1 + ((val_nod - number_of_days[0])*0.5)))
        config["queuesize"] = val_queue
        config["seed"] = val_seed
        config["distributiontype"] = val_disttype
        config["configuration"] = str(run_number) + "_" + str(config_ctr)
        config["threshold"] = val_threshold
        config["dos-number"] = val_dosnumber
        config["jam-tower"] = val_jamtower[0]
        config["jam-tower-logic"] = val_jamtower[1]
        config["slack-hook"] = slack_hook
        config["contact-list"] = val_cl
        config["trust-simulation"] = trust_simulation
        if trust_simulation:
            config["trust-scores"] = val_ts

        config_ctr += 1
        achtung_dict[current_achtung].append(config)
        config = {}

    with open(CONFIG_FILE, 'w') as outfile:
        print("Writing", config_ctr, "files to", CONFIG_FILE)
        json.dump(achtung_dict, fp=outfile, sort_keys=True, indent=2)

    if input("Upload to achtung? 'y' to upload.") == 'y':
        os.system("scp " + CONFIG_FILE + " achtung:moby_simulator/")
        print("Upload complete...")

if __name__ == "__main__":
    main()

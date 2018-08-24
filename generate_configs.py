#!/usr/bin/env python3
import json
import itertools
import os
import os.path
import pdb
from datetime import datetime as dt
###create a directory to store all the configs######
if not os.path.exists(os.getcwd() + '/data/configs'):
    os.makedirs(os.getcwd() + '/data/configs')
else:
    #remove already existing configs
    files = os.listdir(os.getcwd() + '/data/configs')
    for f in files:
        os.remove(os.getcwd() + '/data/configs/' + f)
####################################################

achtungs = ["achtung02", "achtung03", "achtung04", "achtung05", "achtung06", "achtung07", "achtung10", "achtung11", "achtung12", "achtung13", "achtung14", "achtung15", "achtung16", "achtung17"]
achtungpool = itertools.cycle(achtungs)

# Makes keeping track of different runs easier than manually changing this counter.
#YYYYMMDDHHMMSS
run_number = dt.now().strftime("%Y%m%d%H%M%S")
"""
first day of each week in the year 2009 i.e the days which represent all Mondays in 2009

[4, 11, 18, 25, 32, 39, 46, 53, 60, 67, 74, 81, 88, 95, 102, 109, 116, 123, 130, 137, 144, 151, 158, 165, 172, 179, 186, 193, 200, 207, 214, 221, 228, 235, 242, 249, 256, 263, 270, 277, 284, 291, 298, 305, 312, 319, 326, 333, 340, 347, 354, 361]

"""
#ttls = [12, 24, 36, 48, 60, 72]
#ttls needs to be infinite
#ttls = [72]
#ttl needs to be infinite which means it needs to be as much as the duration of the simulation

#start_days = [4, 11, 18, 25, 32, 39, 46, 53, 60, 67, 74, 81, 88, 95, 102, 109, 116, 123, 130, 137, 144, 151, 158, 165, 172, 179, 186, 193, 200, 207, 214, 221, 228, 235, 242, 249, 256, 263, 270, 277,284, 291, 298, 305, 312, 319, 326, 333, 340, 347, 354, 361]
start_days = [4, 11, 18, 25, 32, 39, 46, 53, 60, 67, 74, 81, 88, 95, 102, 109]
number_of_days = [3, 4, 5]
cities = [0]
cooldowns = [24]
number_of_messages = [1000]
#queuesizes = [queuesize for queuesize in xrange(0,max_queue_size + 1,10)]
queuesizes = [0]
seeds = [244896923]
messagegenerationtype = [1] #[1,2]
percentagehoursactive = [50]
deliveryratiotype = [1] #[1,2]
distributiontype = ['uniform', 'user_activity_based', 'total_users_based', 'region_sms_based']
#distributiontype = ['region_sms_based']
#thresholds = [0, 2, 4, 6, 8, 10, 12]
#infinite since we are intially taking an estimate of the possible PDRs
thresholds = [2]
max_number = 10 #max number of dos messages to send
dos_numbers = [number for number in range(1, max_number + 1, 1)]
dos_numbers = [0]
# (% towers to jam, jamming logic)
# jamtower = [(0, 0), (10, 0), (10, 1)] # Different jamming scenarios.

def main():
    config = {}
    config_ctr = 0
    print("Cleaning current config files and writing new ones.")
    for f in achtungs:
        if os.path.isfile(os.getcwd() + '/' + f + '.json'):
            os.remove(f+".json")
    #for val_ttl in ttls:
    for val_start in start_days:
        for val_nod in number_of_days:
            for val_city in cities:
                for val_cd in cooldowns:
                    for val_nm in number_of_messages:
                        for val_queue in queuesizes:
                            for val_seed in seeds:
                                for val_msgtype in messagegenerationtype:
                                    for val_active in percentagehoursactive:
                                        for val_delratio in deliveryratiotype:
                                            for val_disttype in distributiontype:
                                                for val_threshold in thresholds:
                                                    for val_dosnumber in dos_numbers:
                                                        current_achtung = next(achtungpool)
                                                        config["start-day"] = val_start
                                                        config["end-day"] = val_start+val_nod
                                                        config["ttl"] = val_nod * 24
                                                        config["city-number"] = val_city
                                                        config["cooldown"] = val_cd
                                                        config["number"] = val_nm
                                                        config["queuesize"] = val_queue
                                                        config["seed"] = val_seed
                                                        config["messagegenerationtype"] = val_msgtype
                                                        config["percentagehoursactive"] = val_active
                                                        config["deliveryratiotype"] = val_delratio
                                                        config["distributiontype"] = val_disttype
                                                        config["configuration"] = str(run_number) + "_" + str(config_ctr)
                                                        config["threshold"] = val_threshold
                                                        config["sybil-number"] = val_dosnumber
                                                        config_ctr += 1
                                                        with open(current_achtung+".json", 'a+') as outfile:
                                                            outfile.write("!")
                                                            json.dump(config, outfile)
                                                            #keeping track of the parameters used inside configurations to help with graphs
                                                        with open('data/configs/' + config["configuration"] + '.txt', 'w') as out:
                                                            json.dump(config, out)

    pdb.set_trace()
    print("Uploading configs.", config_ctr)
    os.system("scp achtung*.json achtung:moby_simulator/")

    print("Uploading individual configs")
    os.system("scp -r data/configs achtung:moby_simulator/data/")

if __name__ == "__main__":
    main()

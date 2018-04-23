#!/usr/bin/env python
import json
import itertools
import os
import os.path

achtungs = ["achtung02", "achtung03", "achtung04", "achtung05", "achtung06", "achtung07", "achtung12", "achtung13", "achtung14", "achtung15", "achtung16", "achtung17"]
achtungpool = itertools.cycle(achtungs)

run_number = 0
ttls = [12, 24, 36, 48, 60, 72]
start_days = [100]
number_of_days = [3]
cities = [0, 1, 2, 3]
cooldowns = [12, 24, 36]
number_of_messages = [100000]

def main():
    config = {}
    config_ctr = 0
    total_configs = len(ttls) * len(start_days) * len(number_of_days) * len(cities) * len(cooldowns)
    print "Cleaning current config files."
    for f in achtungs:
        if os.path.isfile(os.getcwd() + '/' + f + '.json'):
            os.remove(f+".json")
    for val_ttl in ttls:
        for val_start in start_days:
            for val_nod in number_of_days:
                for val_city in cities:
                    for val_cd in cooldowns:
                        for val_nm in number_of_messages:
                            current_achtung = next(achtungpool)
                            config["ttl"] = val_ttl
                            config["start-day"] = val_start
                            config["end-day"] = val_start+val_nod
                            config["city-number"] = val_city
                            config["cooldown"] = val_cd
                            config["number"] = val_nm
                            config["configuration"] = str(run_number) + "_" + str(config_ctr)
                            config_ctr += 1
                            with open(current_achtung+".json", 'a+') as outfile:
                                outfile.write("!")
                                json.dump(config, outfile)

    print config_ctr, "Uploading configs."
    os.system("scp achtung*.json achtung:moby_simulator/")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import os
import sys
import json
import statistics
import itertools
from collections import defaultdict

SEEDS_DIR = "data/seeds/"
LOGS_DIR = "data/logs/"
RESULTS_DIR = "data/results/"

def main():
    parser = argparse.ArgumentParser(description='Moby message generation script script.')
    parser.add_argument('--configuration', help='Configuration and message file id', type=str, nargs='?', default="")
    args = parser.parse_args(sys.argv[1:])
    conf = args.configuration
    if conf == "":
        print("Please supply a config file with --configuration")
        return
    confs = os.listdir(SEEDS_DIR)
    # Get config files
    confs = list(filter(lambda e: e.startswith(conf), confs))
    confs = list(map(lambda e: e.strip(".config"), confs))
    confs = sorted(confs, key = lambda x: int(x.split("_")[1]))
    # Get log confs
    logs = os.listdir(LOGS_DIR)
    logs = list(filter(lambda e: e.startswith(conf), logs))
    print("Working on", len(confs), "configurations for run number:", conf)
    print(logs)
    if len(logs) != len(confs):
        print("Incomplete configuration :/ logs:", len(logs), " confs:", len(confs))
        return
    sim = confs[0]
    with open(SEEDS_DIR + sim + ".config") as inp:
        conf_params = json.load(inp)
    ttl = conf_params["messages"][0]["ttl"]
    del conf_params["messages"]
    del conf_params["userpool"]
    del conf_params["all-towers"]
    threshold = conf_params["threshold"]
    queuesize = conf_params["queuesize"]
    msg_pat = defaultdict(lambda: defaultdict(int))
    this_hour = -1
    with open(LOGS_DIR + sim + ".nohup") as inp:
        for line in inp:
            if "Delay:" in line:
                latency = int(line.split("Delay:")[1])
                msg_pat[this_hour - latency][latency] += 1
            elif "Sim hour:" in line:
                this_hour += 1
    this_hour = 0
    print(msg_pat)
    with open(RESULTS_DIR + sim + ".csv") as inp:
        for line in inp:
            _, _, _, delivery_count, sent_count, _, _, _, _, _, _, _, _ = line.strip().split(",")
            delivery_count = int(delivery_count)
            sent_count = int(sent_count)
            # avg lat and std dev of lat
            latencies = msg_pat[this_hour]
            lat_lst = []
            for i in latencies.keys():
                for j in range(latencies[i]):
                    lat_lst.append(i)
            if len(lat_lst) > 0:
                avg_lat = statistics.mean(lat_lst)
                if len(lat_lst) > 1:
                    std_dev_lat = statistics.stdev(lat_lst)
                else:
                    std_dev_lat = 0
                print(getline(this_hour, delivery_count, sent_count, avg_lat, std_dev_lat))
            else:
                print(getline(this_hour, delivery_count, sent_count, 0, 0))
            this_hour += 1

def getline(*args):
    retstr = str(args[0])
    dlim = ','
    for i in args[1:]:
        retstr = retstr + dlim + str(i)
    return retstr

if __name__ == "__main__":
        main()

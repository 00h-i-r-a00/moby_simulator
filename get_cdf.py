#!/usr/bin/env python3
import argparse
import os
import sys
import json
import statistics

SEEDS_DIR = "data/seeds/"
LOGS_DIR = "data/logs/"

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
    for sim in confs:
        with open(SEEDS_DIR + sim + ".config") as inp:
            conf_params = json.load(inp)
        ttl = conf_params["messages"][0]["ttl"]
        del conf_params["messages"]
        del conf_params["userpool"]
        del conf_params["all-towers"]
        threshold = conf_params["threshold"]
        queuesize = conf_params["queuesize"]
        lat_lst = []
        with open(LOGS_DIR + sim + ".nohup") as inp:
            for line in inp:
                if "Delay:" in line:
                    latency = int(line.split("Delay:")[1])
                    lat_lst.append(latency)
        stddev = statistics.stdev(lat_lst)
        mean = statistics.mean(lat_lst)
        print(getline(sim, queuesize, threshold, ttl, mean, stddev))

def getline(*args):
    retstr = str(args[0])
    dlim = ','
    for i in args[1:]:
        retstr = retstr + dlim + str(i)
    return retstr

if __name__ == "__main__":
        main()

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
    plot_results = defaultdict(dict)
    for sim in confs:
        with open(SEEDS_DIR + sim + ".config") as inp:
            conf_params = json.load(inp)
        ttl = conf_params["messages"][0]["ttl"]
        with open(RESULTS_DIR + sim + ".csv") as inp:
            _, _, _, delivered, sent, ttl, qs, _, _, trust = inp.readlines()[-1].strip().split(",")[:10]
            dr = float(delivered) / float(sent)
            dr = round(dr, 3)
            logic = conf_params["jam-tower-logic"]
            jamnum = conf_params["jam-tower"]
            key = str(logic) + "_" + str(ttl)
            print(getline([qs, dr, ttl, conf_params["trust-scores"], conf_params["trust-simulation"], conf_params["threshold"], logic, jamnum, len(conf_params["jam-tower-list"])]))
            if conf_params["trust-simulation"] and conf_params["dos-number"] == 10:
                print("^^^^")
            plot_results[key][jamnum] = dr
    print(plot_results)
    epidemic = {12: 0.4633, 24: 0.8448, 36: 0.9499, 48: 0.9744, 60: 0.9786, 72: 0.979}
    marks = ["-", "|", "o", "*", "triangle", "triangle*", "diamond", "diamond*", "square", "square*", "pentagon", "pentagon*"]
    index = 0
    for key, value in plot_results.items():
        kep = key.split("_")
        logic = int(kep[0])
        ttl = int(kep[1])
        print("\\addplot[mark="+marks[index]+"] coordinates{")
        index += 1
        for k, v in value.items():
            res = round(float(v) / epidemic[ttl], 3)
            print("(", k, ",", res,") %", v, epidemic[ttl])
        print("};")
        if logic == 0:
            print("\\addlegendentry{TTL:" + str(ttl) + " Random Jamming}")
        else:
            print("\\addlegendentry{TTL:" + str(ttl) + " Popularity Oracle}")

def getline(args):
    retstr = str(args[0])
    dlim = ','
    for i in args[1:]:
        retstr = retstr + dlim + str(i)
    return retstr

if __name__ == "__main__":
        main()

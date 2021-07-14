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
    for sim in confs:
        with open(SEEDS_DIR + sim + ".config") as inp:
            conf_params = json.load(inp)
        ttl = conf_params["messages"][0]["ttl"]
        # dellst = ["messages", "userpool", "alluserslen", "userpoollen", "city", "start-day", "end-day", "distributiontype", "jam-tower", "jam-tower-logic", "slack-hook", "cooldown", "jam-tower-list", "jam-user", "jam-user-logic", "jam-user-list"]
        # for i in dellst:
        #     del conf_params[i]
        detlst = ["threshold", "jam-tower", "jam-tower-logic"]
        # print("All towers len:", len(conf_params["all-towers"]))
        conf_dets = []
        for i in detlst:
            conf_dets.append(conf_params[i])
        # print(conf_params)
        if conf_params["trust-scores"] == "3hop1thresh":
            continue
        with open(RESULTS_DIR + sim + ".csv") as inp:
            _, _, _, delivered, sent, ttl, qs, _, _, trust = inp.readlines()[-1].strip().split(",")[:10]
            dr = float(delivered) / float(sent)
            dr = round(dr, 3)
        print(getline([qs, dr, ttl, conf_dets[0], conf_dets[1]]))

def getline(args):
    retstr = str(args[0])
    dlim = ','
    for i in args[1:]:
        retstr = retstr + dlim + str(i)
    return retstr

if __name__ == "__main__":
        main()

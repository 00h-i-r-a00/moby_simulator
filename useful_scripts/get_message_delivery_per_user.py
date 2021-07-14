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
    parser = argparse.ArgumentParser(description='Script to count message delivery based on senders.')
    parser.add_argument('--configuration', help='Configuration and message file id', type=str, nargs='?', default="")
    parser.add_argument('--percentage', help='Percentage of top users considered malicious', type=int, nargs='?', default=0)
    args = parser.parse_args(sys.argv[1:])
    conf = args.configuration
    percentage = args.percentage
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
    if len(logs) != len(confs):
        print("Incomplete configuration :/ logs:", len(logs), " confs:", len(confs))
        return
    for sim in confs:
        print("Simulation:", sim)
        with open(SEEDS_DIR + sim + ".config") as inp:
            conf_params = json.load(inp)
        msgs = conf_params["messages"]
        threshold = int(conf_params["threshold"])
        queuesize = conf_params["queuesize"]
        lat_lst = []
        delivery_dict = defaultdict(int)
        # Could read this from the .md result file, but since we have this in place, might as well use it.
        delivered = 0
        with open(LOGS_DIR + sim + ".nohup") as inp:
            for line in inp:
                if "Delay:" in line:
                    msg_id = int(line.split(" ")[1])
                    # Messages array must be sorted, but better double check and crash!
                    msg_dets = msgs[msg_id]
                    if msg_dets["id"] != msg_id:
                        print("Message ID and message array element mismatch :/")
                        return
                    delivery_dict[int(msg_dets["src"])] += 1
                    delivered += 1
        result = sorted(delivery_dict.items(), key=lambda v: v[1], reverse=True)
        if percentage != 0:
            index = int((percentage/100) * len(result))
            print("Index:", index)
        else:
            index = 0
        counted = 0
        for e in result[index:]:
            counted += e[1]
        print("Counted:", counted, "Total:", delivered, "Percentage:", float(counted/delivered))
        # print("Delivery per user:", result)
        # print("Total delivered:", delivered)

def getline(*args):
    retstr = str(args[0])
    dlim = ','
    for i in args[1:]:
        retstr = retstr + dlim + str(i)
    return retstr

if __name__ == "__main__":
        main()

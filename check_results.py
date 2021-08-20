#!/usr/bin/env python3
import argparse
from collections import defaultdict
import glob
import json
import os
import sys

RESULTS_DIR = "data/results/"
RESULTS_EXT = ".csv"
MESSAGE_DELAYS_EXT = '.md'
QUEUE_OCCUPANCY_EXT = '.qo'

CONFIG_FILE = "config.json"

def main():
    parser = argparse.ArgumentParser(description='Moby result completion checker.')
    parser.add_argument('--run-number', help='Run number to be checked.', type=int, nargs='?', default=0)
    args = parser.parse_args(sys.argv[1:])
    run_number = args.run_number
    configs = {}
    incomplete = defaultdict(list)
    all_configs = 0
    with open(CONFIG_FILE) as inf:
        configs = json.load(inf)
    for achtung in configs.keys():
        all_configs += len(config[achtung])
        for config in configs[achtung]:
            configuration = config["configuration"]
            if str(run_number) not in configuration:
                continue
            results = [RESULTS_DIR + configuration + i for i in [RESULTS_EXT, MESSAGE_DELAYS_EXT, QUEUE_OCCUPANCY_EXT]]
            for result_file in results:
                if not os.path.exists(result_file):
                    incomplete[achtung].append(configuration)
                    break
    total = 0
    for k in incomplete.keys():
        total += len(incomplete[k])
        print("Incomplete for: ", k, len(incomplete[k]), incomplete[k])
    print("Total incomplete: ", total, " of:", all_configs)

if __name__ == "__main__":
        main()

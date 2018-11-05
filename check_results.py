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

def main():
    parser = argparse.ArgumentParser(description='Moby result completion checker.')
    parser.add_argument('--run-number', help='Run number to be checked.', type=int, nargs='?', default=0)
    args = parser.parse_args(sys.argv[1:])
    run_number = args.run_number
    files = glob.glob('*.json')
    configs = {}
    incomplete = defaultdict(list)
    all_configs = 0
    for f in files:
        with open(f) as conf_file:
            confs = json.load(conf_file)
            configs[f.strip('.json')] = confs
            all_configs += len(confs)
    for achtung in configs.keys():
        for config in configs[achtung]:
            configuration = config["configuration"]
            if str(run_number) not in configuration:
                continue
            results = [RESULTS_DIR + configuration + i for i in [RESULTS_EXT, MESSAGE_DELAYS_EXT, QUEUE_OCCUPANCY_EXT]]
            for result_file in results:
                if not os.path.exists(result_file):
                    incomplete[achtung].append(configuration[15:])
                    break
    total = 0
    for k in incomplete.keys():
        total += len(incomplete[k])
        print("Incomplete for: ", k, len(incomplete[k]), incomplete[k])
    print("Total incomplete: ", total, " of:", all_configs)

if __name__ == "__main__":
        main()

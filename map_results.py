#!/usr/bin/env python3
import argparse
from prettytable import PrettyTable
import os
import sys

RESULTS_PREFIX = 'data/results/'
RESULT_EXT = '.csv'
MESSAGE_DELAYS_EXT = '_message_delays.csv'
QUEUE_OCCUPANCY_EXT = '_queue_occupancy.csv'

def main():
    table = PrettyTable()
    parser = argparse.ArgumentParser(description='Moby results visualizer.')
    parser.add_argument('--run-number', help='Run number to be plotted.', type=int, nargs='?', default=0)
    args = parser.parse_args(sys.argv[1:])
    run_number = args.run_number
    files = os.listdir(RESULTS_PREFIX)
    filtered_files = []
    for f in files:
        if f.startswith(str(run_number)) and f.endswith(RESULT_EXT) and (not f.endswith(MESSAGE_DELAYS_EXT)) and (not f.endswith(QUEUE_OCCUPANCY_EXT)):
            filtered_files.append(f.strip(RESULT_EXT))
    print("Plotting results for:", filtered_files)

if __name__ == "__main__":
    main()

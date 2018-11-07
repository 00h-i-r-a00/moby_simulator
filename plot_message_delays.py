#!/usr/bin/env python3
import argparse
from collections import defaultdict
import numpy as np
import os
import matplotlib.pyplot as plt
import sys

RESULTS_PREFIX = 'data/results/'
REPORTS_PREFIX = 'data/reports/'
MESSAGE_DELAYS_EXT = '.md'

def main():
    parser = argparse.ArgumentParser(description='Script to plot moby message delays into a histogram.')
    parser.add_argument('--run-number', help='Run number to be plotted.', type=str, nargs='?', default="")
    parser.add_argument('--quiet', help='Wether to call show or not.', type=bool, nargs='?', default=False)
    args = parser.parse_args(sys.argv[1:])
    run_number = args.run_number
    quiet = args.quiet
    data_file = RESULTS_PREFIX + run_number + MESSAGE_DELAYS_EXT
    REPORT_DIR = REPORTS_PREFIX + run_number.split("_")[0] + "/"
    print("Plotting bar chart for:", run_number)
    msgs_seen = []
    delays = defaultdict(int)
    with open(data_file, 'r') as infile:
        for line in infile:
            msg_id, delay = line.split(',')
            delay = int(delay)
            if msg_id in msgs_seen:
                print("Found a duplicate!!", msg_id)
            else:
                msgs_seen.append(msg_id)
                delays[delay] += 1
    x_vals = []
    y_vals = []
    for i in range(0, max(delays.keys())):
        x_vals.append(i)
        y_vals.append(delays[i])
    print(x_vals, y_vals)
    plt.bar(x_vals, y_vals)
    plt.xlabel("Delays")
    plt.ylabel("Number of messages with delay")
    plt.title("Message delays for run" + run_number)
    if not quiet:
        plt.show()
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
    plt.savefig(REPORT_DIR + run_number.split("_")[-1] + ".eps", format="eps", dpi=1200)

if __name__ == "__main__":
    main()

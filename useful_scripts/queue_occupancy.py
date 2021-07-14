#!/usr/bin/env python3
from collections import defaultdict
import argparse
import sys
import glob

RESULTS_DIR = "data/results/"
QUEUE_OCCUPANCY_EXT = '.qo'
QUEUE_AGG_EXT = '.qa'

queue_sizes = defaultdict(int)
max_queue_size = defaultdict(int)
users = defaultdict(int)

def main():
    parser = argparse.ArgumentParser(description='Moby result completion checker.')
    parser.add_argument('--run-number', help='Run number to be checked.', type=int, nargs='?', default=0)
    args = parser.parse_args(sys.argv[1:])
    run_number = args.run_number
    files = glob.glob(RESULTS_DIR + str(run_number) + "*" + QUEUE_OCCUPANCY_EXT)
    minday = 500
    maxday = 0
    for f in files:
        print("Processing file:", f)
        with open(f) as qof:
            for line in qof:
                day, hour, uid, qs = line.split(",")
                key = day + "_" + hour
                day = int(day)
                qs = int(qs)
                minday = min(day, minday)
                maxday = max(day, maxday)
                queue_sizes[key] += qs
                users[key] += 1
                max_queue_size[key] = max(max_queue_size[key], qs)
        with open(f.replace(QUEUE_OCCUPANCY_EXT, QUEUE_AGG_EXT), "w") as qaf:
            print("Writing file: ", f.replace(QUEUE_OCCUPANCY_EXT, QUEUE_AGG_EXT))
            for i in range(minday, maxday+1):
                for j in range(24):
                    key = str(i) + "_" + str(j)
                    avg = queue_sizes[key] / users[key]
                    qaf.write(getline(day, hour, avg, max_queue_size[key]))

def getline(*args):
    retstr = str(args[0])
    dlim = ','
    for i in args[1:]:
        retstr = retstr + dlim + str(i)
    retstr += '\n'
    return retstr

if __name__ == "__main__":
    main()

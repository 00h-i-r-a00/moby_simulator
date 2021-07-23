#!/usr/bin/env python3
import sys
import math

def main():
    if len(sys.argv) <= 1:
        print("Input towers file as cli arg...")
    infile = sys.argv[1]
    towers = {}
    with open(infile, "r") as inf:
        line = inf.readline()
        while line:
            id, lat, lon, _ = line.strip().split(" ")
            towers[id] = (lat, lon)
            line = inf.readline()
    print(towers)

if __name__ == "__main__":
    main()

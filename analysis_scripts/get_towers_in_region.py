#!/usr/bin/env python
import math
import sys

threshold = 0.07
c = ["Madrid", "Barcelona", "Valencia", "Seville"]
x = [40.383333, 41.383333, 39.4229, 37.3766]
y = [-3.716667,  2.183333, -0.3522, -5.9260]


def main():
    infile = sys.argv[1]
    for i in xrange(0,4):
        print "Extracting towers in ", infile,"for: ", c[i], " ", x[i], " ", y[i]
        with open(infile) as data, open("towers_"+str(i), "w+") as outfile:
            for entry in data:
                line = entry.strip().split(' ')
                tower_id = line[0]
                tower_lat = float(line[1])
                tower_long = float(line[2])
                dist = math.sqrt((x[i] - tower_lat)**2 + (y[i] - tower_long)**2)
                if(dist < threshold):
                    outfile.write(entry)

if __name__ == "__main__":
    main()

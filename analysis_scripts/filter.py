#!/usr/bin/env python
import sys

def main():
    days = sys.argv[1:]
    print "Processing days: ", days
    towers = []
    with open("towers") as data:
        for entry in data:
            tid = entry.split()[0]
            towers.append(tid)
    print "Found towers: ", len(towers)
    for i in xrange(0, len(days)):
        print "Splitting ", days[i], " based on hours"
        with open(days[i]) as data:
            for entry in data:
                hour, tid, users = entry.strip().split(',')
                if tid in towers:
                    with open(str(i)+"_"+hour+".twr", "a+") as outfile:
                        outfile.write(entry)
            print "Done with ", days[i]

if __name__ == "__main__":
    main()

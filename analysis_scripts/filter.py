#!/usr/bin/env python
import sys

def main():
    days = sys.argv[1:]
    print "Processing days: ", days
    towers_by_city = []
    for i in xrange(0, 4):
        towers = []
        towers_file = "towers_" + str(i)
        with open(towers_file) as data:
            for entry in data:
                tid = entry.split()[0]
                towers.append(tid)
        towers_by_city.append(towers)
    for i in xrange(0, 4):
        print "Found towers: ", len(towers_by_city[i]), i
    for i in xrange(0, len(days)):
            print "Splitting ", days[i], " based on hours"
            with open(days[i]) as data:
                for entry in data:
                    hour, tid, users = entry.strip().split(',')
                    for j in xrange(0, 4):
                        if tid in towers:
                            with open("data/"+str(j)+"/"+str(i)+"_"+hour+".twr", "a+") as outfile:
                                outfile.write(entry)
                print "Done with ", days[i]

if __name__ == "__main__":
    main()

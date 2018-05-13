#!/usr/bin/env python
import sys, pandas

days_of_the_year = [d.strftime('%Y%m%d') for d in pandas.date_range('20090101','20091231')]
COMMS_PREFIX = "nb_communications_per_tower_per_user_per_hour_"
COMMS_EXT = ".csv.bz2.csv"

def main():
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
    for day in days_of_the_year:
        commsfile = COMMS_PREFIX + str(day) + COMMS_EXT
        print "Processing", commsfile
        with open(commsfile) as infile:
            for entry in infile:
                hour, tid, user, call, sms = entry.strip().split(',')
                for j in xrange(0, 4):
                    if tid in towers_by_city[j]:
                        with open("data/"+str(j)+"/"+str(day)+".comms", "a+") as outfile:
                            outfile.write(entry)

if __name__ == "__main__":
    main()

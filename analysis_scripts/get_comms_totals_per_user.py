#!/usr/bin/env python
import pandas
from collections import defaultdict

start_day = '20090101'
end_day = '20091231'
days_of_the_year = [d.strftime('%Y%m%d') for d in pandas.date_range(start_day,end_day)]
COMMS_EXT = ".comms"
COMMS_AGG_EXT = ".comuser"

def main():
    day_ctr = 0
    for day in days_of_the_year:
        print "Processing day:", day
        commsfile = str(day) + COMMS_EXT
        with open(commsfile) as infile:
            user_calls_counter = defaultdict(int)
            user_sms_counter = defaultdict(int)
            hour_old = 0
            for entry in infile:
                hour, tid, user, call, sms = entry.strip().split(',')
                if hour_old == int(hour):
                    user_calls_counter[user] += int(call)
                    user_sms_counter[user] += int(sms)
                else:
                    with open(str(day_ctr) + COMMS_AGG_EXT, "a+") as outfile:
                        for u in user_calls_counter.iterkeys():
                            outfile.write(getline(hour_old, u, user_calls_counter[u], user_sms_counter[u]))
                            outfile.write("\n")
                    user_sms_counter = defaultdict(int)
                    user_calls_counter = defaultdict(int)
                    hour_old = int(hour)
            with open(str(day_ctr) + COMMS_AGG_EXT, "a+") as outfile:
                for u in user_calls_counter.iterkeys():
                    outfile.write(getline(hour_old, u, user_calls_counter[u], user_sms_counter[u]))
                    outfile.write("\n")
            day_ctr += 1

def getline(*args):
    retstr = str(args[0])
    dlim = ','
    for i in args[1:]:
        retstr = retstr + dlim + str(i)
    return retstr

if __name__ == "__main__":
    main()

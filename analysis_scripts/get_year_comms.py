#!/usr/bin/env python
import pandas
from bz2 import BZ2File as bzopen

start_day = '20090101'
end_day = '20091231'
days_of_the_year = [d.strftime('%Y%m%d') for d in pandas.date_range(start_day,end_day)]
file_start = "/net/data/moby/level_1/nb_comms_per_tower_per_user-renumbered-1year/nb_communications_per_tower_per_user_per_hour_"
file_end = ".csv.bz2"

def main():
    call_ctr = 0
    sms_ctr = 0
    for day in days_of_the_year:
        print("Processing day:", day)
        commsfile = file_start + day + file_end
        with bzopen(commsfile) as infile:
            print(infile.readline())
            for entry in infile:
                hour, tid, user, call, sms = entry.strip().split(',')
                call_ctr += int(call)
                sms_ctr += int(sms)
    print("Total comms for the year, calls:", call_ctr, "sms:", sms_ctr)

if __name__ == "__main__":
    main()

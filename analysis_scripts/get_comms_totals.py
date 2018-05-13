#!/usr/bin/env python
import pandas

start_day = '20090101'
end_day = '20091231'
days_of_the_year = [d.strftime('%Y%m%d') for d in pandas.date_range(start_day,end_day)]
COMMS_EXT = ".comms"
COMMS_AGG_EXT = ".comagg"

def main():
    day_ctr = 0
    for day in days_of_the_year:
        print "Processing day:", day
        commsfile = str(day) + COMMS_EXT
        with open(commsfile) as infile:
            tower_set = set()
            user_set = set()
            call_ctr = 0
            sms_ctr = 0
            hour_old = 0
            for entry in infile:
                hour, tid, user, call, sms = entry.strip().split(',')
                if hour_old == int(hour):
                    tower_set.add(tid)
                    user_set.add(user)
                    call_ctr += int(call)
                    sms_ctr += int(sms)
                else:
                    with open(str(day_ctr) + COMMS_AGG_EXT, "a+") as outfile:
                        outfile.write(str(hour_old) + "," + str(len(tower_set)) + "," + str(len(user_set)) + "," + str(call_ctr) + "," + str(sms_ctr))
                        outfile.write("\n")
                    tower_set = set()
                    user_set = set()
                    call_ctr = 0
                    sms_ctr = 0
                    hour_old = int(hour)
            with open(str(day_ctr) + COMMS_AGG_EXT, "a+") as outfile:
                        outfile.write(str(hour_old) + "," + str(len(tower_set)) + "," + str(len(user_set)) + "," + str(call_ctr) + ",  " + str(sms_ctr))
                        outfile.write("\n")
            day_ctr += 1

if __name__ == "__main__":
    main()

#!/usr/bin/env python
import sys, pandas
import matplotlib.pyplot as plt

days_of_the_year = [d.strftime('%Y%m%d') for d in pandas.date_range('20090101','20090112')]
COMMS_EXT = ".comms"

def main():
    towerlens = []
    userlens = []
    calls = []
    smss = []
    for day in days_of_the_year:
        commsfile = str(day) + COMMS_EXT
        tower_set = set()
        user_set = set()
        call_ctr = 0
        sms_ctr = 0
        with open(commsfile) as infile:
            for entry in infile:
                hour, tid, user, call, sms = entry.strip().split(',')
                tower_set.add(tid)
                user_set.add(user)
                call_ctr += int(call)
                sms_ctr += int(sms)
        towerlens.append(len(tower_set))
        userlens.append(len(user_set))
        calls.append(call_ctr)
        smss.append(sms_ctr)
        print "towers, users, calls, sms", len(tower_set), len(user_set), call_ctr, sms_ctr
    print "Plotting", towerlens, userlens, calls, smss

    plt.figure(1)

    plt.xlabel("Days")
    plt.ylabel("Number of Towers seen.")
    xaxis = [i for i in xrange(len(towerlens))]
    plt.plot(xaxis, towerlens, marker='o')
    plt.show()
    plt.gcf().clear()

    plt.xlabel("Days")
    plt.ylabel("Number of users seen.")
    plt.plot(xaxis, userlens, marker='o')
    plt.show()
    plt.gcf().clear()

    plt.xlabel("Days")
    plt.ylabel("Number of calls made in all towers.")
    plt.plot(xaxis, calls, marker='o')
    plt.show()
    plt.gcf().clear()

    plt.xlabel("Days")
    plt.ylabel("Number of SMSs sent in all towers.")
    plt.plot(xaxis, smss, marker='o')
    plt.show()
    plt.gcf().clear()

if __name__ == "__main__":
    main()

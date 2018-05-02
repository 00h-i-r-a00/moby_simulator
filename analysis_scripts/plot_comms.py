#!/usr/bin/env python
import sys, pandas
import matplotlib.pyplot as plt

start_day = '20090101'
end_day = '20090201'
days_of_the_year = [d.strftime('%Y%m%d') for d in pandas.date_range(start_day,end_day)]
days_to_plot = [d.strftime('%m%d') for d in pandas.date_range(start_day,end_day)]
COMMS_EXT = ".comms"

def main():
    towerlens = []
    towerlensagg = []
    userlens = []
    userlensagg = []
    calls = []
    callsagg = []
    smss = []
    smssagg = []
    for day in days_of_the_year:
        print "Processing day:", day
        commsfile = str(day) + COMMS_EXT
        tower_set = set()
        tower_set_aggrigate = set()
        user_set = set()
        user_set_aggrigate = set()
        call_ctr = 0
        call_ctr_aggrigate = 0
        sms_ctr = 0
        sms_ctr_aggrigate = 0
        with open(commsfile) as infile:
            hour_old = 0
            for entry in infile:
                hour, tid, user, call, sms = entry.strip().split(',')
                tower_set_aggrigate.add(tid)
                user_set_aggrigate.add(user)
                call_ctr_aggrigate += int(call)
                sms_ctr_aggrigate += int(sms)
                if hour_old == int(hour):
                    tower_set.add(tid)
                    user_set.add(user)
                    call_ctr += int(call)
                    sms_ctr += int(sms)
                else:
                    hour_old = int(hour)
                    towerlens.append(len(tower_set))
                    userlens.append(len(user_set))
                    calls.append(call_ctr)
                    smss.append(sms_ctr)
            towerlensagg.append(len(tower_set_aggrigate))
            userlensagg.append(len(user_set_aggrigate))
            callsagg.append(call_ctr_aggrigate)
            smssagg.append(sms_ctr_aggrigate)
    print "Plotting"
    plt.figure(1)
    plt.style.use('ggplot')

    plt.title("Number of towers seen over the days.(" + str(start_day) + "_" + str(end_day) + ")")
    plt.xlabel("Days")
    plt.ylabel("Number of Towers seen.")
    xaxis = [i for i in xrange(len(days_to_plot))]
    plt.plot(xaxis, towerlensagg, marker='o')
    plt.xticks(rotation=45)
    plt.xticks(xaxis, days_to_plot)
    plt.grid()
    plt.show()
    plt.savefig("towers_days" + str(start_day) + "_" + str(end_day) + ".png")
    plt.gcf().clear()

    plt.title("Number of users seen corresponding to all towers seen over the days.(" + str(start_day) + "_" + str(end_day) + ")")
    plt.xlabel("Days")
    plt.ylabel("Number of Users seen.")
    plt.plot(xaxis, userlensagg, marker='o')
    plt.xticks(xaxis, days_to_plot)
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()
    plt.savefig("users_days" + str(start_day) + "_" + str(end_day) + ".png")
    plt.gcf().clear()

    plt.title("Number of calls made by all users among all towers over the days.(" + str(start_day) + "_" + str(end_day) + ")")
    plt.xlabel("Days")
    plt.ylabel("Number of Calls made in all towers.")
    plt.plot(xaxis, callsagg, marker='o')
    plt.xticks(xaxis, days_to_plot)
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()
    plt.savefig("calls_days" + str(start_day) + "_" + str(end_day) + ".png")
    plt.gcf().clear()

    plt.title("Number of text messages sent by all users in all towers over the days.(" + str(start_day) + "_" + str(end_day) + ")")
    plt.xlabel("Days")
    plt.ylabel("Number of SMSs sent in all towers.")
    plt.plot(xaxis, smssagg, marker='o')
    plt.xticks(xaxis, days_to_plot)
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()
    plt.savefig("texts_days" + str(start_day) + "_" + str(end_day) + ".png")
    plt.gcf().clear()

    plt.title("Number of towers seen over the hours.(" + str(start_day) + "_" + str(end_day) + ")")
    plt.xlabel("Hours")
    plt.ylabel("Number of Towers seen.")
    xaxis = [i for i in xrange(len(towerlens))]
    plt.plot(xaxis, towerlens, marker='o')
    plt.grid()
    plt.show()
    plt.savefig("towers_hours" + str(start_day) + "_" + str(end_day) + ".png")
    plt.gcf().clear()

    plt.title("Number of users seen corresponding to all towers over the hours.(" + str(start_day) + "_" + str(end_day) + ")")
    plt.xlabel("Hours")
    plt.ylabel("Number of users seen.")
    plt.plot(xaxis, userlens, marker='o')
    plt.grid()
    plt.show()
    plt.savefig("users_hours" + str(start_day) + "_" + str(end_day) + ".png")
    plt.gcf().clear()

    plt.title("Number of calls made by all users seen among all towers over the hours.(" + str(start_day) + "_" + str(end_day) + ")")
    plt.xlabel("Hours")
    plt.ylabel("Number of calls made in all towers.")
    plt.plot(xaxis, calls, marker='o')
    plt.grid()
    plt.show()
    plt.savefig("calls_hours" + str(start_day) + "_" + str(end_day) + ".png")
    plt.gcf().clear()

    plt.title("Number of text messages sent by all users in all towers over the hours.(" + str(start_day) + "_" + str(end_day) + ")")
    plt.xlabel("Hours")
    plt.ylabel("Number of SMSs sent in all towers.")
    plt.plot(xaxis, smss, marker='o')
    plt.grid()
    plt.show()
    plt.savefig("texts_hours" + str(start_day) + "_" + str(end_day) + ".png")
    plt.gcf().clear()

if __name__ == "__main__":
    main()

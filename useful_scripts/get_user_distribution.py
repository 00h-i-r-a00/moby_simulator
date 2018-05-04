#!/usr/bin/env python
from collections import defaultdict
from statistics import mean, median, mode, variance

DATA_FILE_PREFIX = "../data/"
DATA_FILE_FORMAT = ".twr"
CONFIGURATION_FILE_FORMAT = ".config"
message_id_start = DATA_FILE_PREFIX

def main():
    userpool = defaultdict(int)
    active_userpool_per_hour = defaultdict(int)
    city = 0
    h = 0
    for current_day in xrange(100, 103):
        for current_hour in xrange(0,24):
            messages_sent_this_hour = 0
            current_data_file = DATA_FILE_PREFIX + str(city) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
            users_this_hour = []
            user_tower_list = defaultdict(list)
            with open(current_data_file) as data:
                for entry in data:
                    hour, tower_id, user_ids = entry.split(",")
                    user_ids = user_ids.strip()
                    users_this_hour += user_ids.split("|")
                    print len(users_this_hour), len(set(users_this_hour))
                    messages_sent_this_hour += len(users_this_hour)
                    for u in set(users_this_hour):
                        user_tower_list[u] += tower_id
            print "Messages for the ", h, "th hour is:", messages_sent_this_hour
            users_this_hour = set(users_this_hour)
            unique_towers_by_all_users = 0
            val_set = []
            for user, tower_list in user_tower_list.iteritems():
                unique_towers_by_all_users += len(set(tower_list))
                val_set.append(len(set(tower_list)))
            m1 = mean(val_set)
            m2 = median(val_set)
            m3 = mode(val_set)
            m4 = max(val_set)
            v1 = variance(val_set)
            print "Mean, Median, Mode, Max, Var", m1, m2, m3, m4, v1
            print "Users seen:", len(users_this_hour)
            print "Unique towers by all users:", unique_towers_by_all_users
            print "opline: ", messages_sent_this_hour, len(users_this_hour), unique_towers_by_all_users, m1, m2, m3, m4
            active_userpool_per_hour[h] = users_this_hour
            h += 1
            for u in users_this_hour:
                userpool[u] += 1

if __name__ == "__main__":
    main()

#!/usr/bin/env python
import sys, random

DATA_FILE_PREFIX = "data/0/"
DATA_FILE_FORMAT = ".twr"
MESSAGE_FILE_FORMAT = ".msg"
start_day = 0
end_day = 1
MESSAGES_TO_GENERATE = 100
message_id_start = DATA_FILE_PREFIX

def main():
    for current_day in xrange(start_day, end_day):
        for current_hour in xrange(0,24):
            current_data_file = DATA_FILE_PREFIX + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
            current_message_file = DATA_FILE_PREFIX + str(current_day) + "_" + str(current_hour) + MESSAGE_FILE_FORMAT
            users_this_hour = []
            print "Generating messages for hour: " + str(current_hour)
            with open(current_data_file) as data:
                for entry in data:
                    hour, tower_id, user_ids = entry.split(",")
                    user_ids = user_ids.strip()
                    users_this_hour += user_ids.split("|")
            print "Users in all towers(double counted):", len(users_this_hour)
            users_this_hour = set(users_this_hour)
            print "Unique users seen this hour: ", len(users_this_hour)
            print "Generating: ", current_message_file, MESSAGES_TO_GENERATE
            # ID, TTL, Source, Destination, hop, trust
            with open(current_message_file, "w") as out_file:
                for i in xrange(0, MESSAGES_TO_GENERATE):
                    id = DATA_FILE_PREFIX + str(current_hour) + "_" + str(i)
                    src, dst = random.sample(users_this_hour, 2)
                    src = str(src)
                    dst = str(dst)
                    ttl = "72"
                    hop = "0"
                    trust = "1"
                    dlim = ","
                    out_file.write(id + dlim + ttl + dlim + src + dlim + dst + dlim + hop + dlim + trust)
                    out_file.write("\n")

if __name__ == "__main__":
    main()

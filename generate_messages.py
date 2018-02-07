#!/usr/bin/env python
import sys, random, argparse

DATA_FILE_PREFIX = "data/"
DATA_FILE_FORMAT = ".twr"
MESSAGE_FILE_FORMAT = ".msg"
start_day = 0
end_day = 3
message_id_start = DATA_FILE_PREFIX

def main():
    parser = argparse.ArgumentParser(description='Moby message generation script script.')
    parser.add_argument('--number', help='Number of messages to generate', type=int, nargs='?', default=1000)
    args = parser.parse_args(sys.argv[1:])
    number_of_messages = args.number
    for city in xrange(0, 4):
        for current_day in xrange(start_day, end_day):
            for current_hour in xrange(0,24):
                current_data_file = DATA_FILE_PREFIX + str(city) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
                current_message_file = DATA_FILE_PREFIX + str(city) + "/" + str(current_day) + "_" + str(current_hour) + MESSAGE_FILE_FORMAT
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
                print "Generating: ", current_message_file, number_of_messages
                # ID, TTL, Source, Destination, hop, trust
                with open(current_message_file, "w") as out_file:
                    for i in xrange(0, number_of_messages):
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

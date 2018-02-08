#!/usr/bin/env python
import sys, random, argparse
from collections import defaultdict

DATA_FILE_PREFIX = "data/"
SEED_FILE_PREFIX = "data/seeds/"
DATA_FILE_FORMAT = ".twr"
MESSAGE_FILE_FORMAT = ".msg"
message_id_start = DATA_FILE_PREFIX

def main():
    userpool = defaultdict(int)
    parser = argparse.ArgumentParser(description='Moby message generation script script.')
    parser.add_argument('--number', help='Number of messages to generate', type=int, nargs='?', default=1000)
    parser.add_argument('--start-day', help='start day of the year', type=int, nargs='?', default=0)
    parser.add_argument('--end-day', help='end day of the year', type=int, nargs='?', default=3)
    parser.add_argument('--timestamp', help='Timestamp to mark logging with', type=int, nargs='?', default=0)
    parser.add_argument('--city', help='City to generate messages for', type=int, nargs='?', default=0)
    parser.add_argument('--threshold', help='Minimum occourances to be considered a legit user', type=int, nargs='?', default=0)
    args = parser.parse_args(sys.argv[1:])
    number_of_messages = args.number
    start_day = args.start_day
    end_day = args.end_day
    timestamp = args.timestamp
    city = args.city
    threshold = args.threshold
    print "Configuration (start, end, number): ", start_day, end_day, number_of_messages
    for current_day in xrange(start_day, end_day):
        for current_hour in xrange(0,24):
            current_data_file = DATA_FILE_PREFIX + str(city) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
            users_this_hour = []
            with open(current_data_file) as data:
                for entry in data:
                    hour, tower_id, user_ids = entry.split(",")
                    user_ids = user_ids.strip()
                    users_this_hour += user_ids.split("|")
            users_this_hour = set(users_this_hour)
            for u in users_this_hour:
                userpool[u] += 1
    dellist = []
    for key, value in userpool.iteritems():
        if value <= threshold:
            dellist.append(key)
    print "Total users seen: ", len(userpool)
    for u in dellist:
        del userpool[u]
    print "Users above threshold: ", len(userpool)
    current_message_file = SEED_FILE_PREFIX + str(start_day) + "_" + str(end_day) + "_" + str(timestamp) + MESSAGE_FILE_FORMAT
    print "Generating: ", current_message_file
    # ID, TTL, Source, Destination, hop, trust
    with open(current_message_file, "a+") as out_file:
        for i in xrange(0, number_of_messages):
            id = DATA_FILE_PREFIX + str(current_hour) + "_" + str(i)
            src, dst = random.sample(userpool.keys(), 2)
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

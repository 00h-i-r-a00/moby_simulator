#!/usr/bin/env python
from collections import defaultdict

DATA_FILE_PREFIX = "users_per_tower_per_hour_20090319_"
DATA_FILE_FORMAT = ".csv"

class Message:
    def __init__(self, id, ttl, src, dst, hop, trust):
        self.id  = id
        self.ttl = ttl
        self.src = src
        self.dst = dst
        seld.hop = hop
        self.trust = trust

def main():
    network_state = defaultdict(set)
    message_queue = defaultdict(set)
    for current_hour in xrange(0,24):
        current_data_file = DATA_FILE_PREFIX + str(current_hour) + DATA_FILE_FORMAT
        users_this_hour = []
        print "Processing hour: " + str(current_hour)
        with open(current_data_file) as data:
            for entry in data:
                hour, tower_id, user_ids = entry.split(",")
                user_ids = user_ids.strip()
                previous_state = network_state[tower_id]
                users_this_hour += user_ids.split("|")
                new_state = set(user_ids.split("|"))
                transitions_added = new_state.difference(previous_state)
                transitions_removed = previous_state.difference(new_state)
                transitions_idle = new_state.intersection(previous_state)
                network_state[tower_id] = new_state
                # print "Added: ", transitions_added
                # print "Removed: ", transitions_removed
        print "Users in all towers(double counted):", len(users_this_hour)
        print "Users seen this hour: ", len(set(users_this_hour))
        print "States updated. Sending a few messages around."

if __name__ == "__main__":
    main()

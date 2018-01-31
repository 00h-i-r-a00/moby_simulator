#!/usr/bin/env python
from collections import defaultdict

DATA_FILE_PREFIX = "users_per_tower_per_hour_20090319_"
DATA_FILE_FORMAT = ".csv"
MESSAGE_FILE_FORMAT = ".msg"

network_state_old = defaultdict(set)
network_state_new = defaultdict(set)
message_queue = defaultdict(list)
dirty_nodes = []

class Message:
    def __init__(self, id, ttl, src, dst, hop, trust):
        self.id  = id
        self.ttl = ttl
        self.src = src
        self.dst = dst
        self.hop = hop
        self.trust = trust

def main():
    first_state = True
    for current_hour in xrange(0,6):
        global dirty_nodes
        dirty_nodes = []
        current_data_file = DATA_FILE_PREFIX + str(current_hour) + DATA_FILE_FORMAT
        current_message_file = DATA_FILE_PREFIX + str(current_hour) + MESSAGE_FILE_FORMAT
        users_this_hour = []
        print "Processing hour: " + str(current_hour)
        with open(current_data_file) as data:
            for entry in data:
                # Just calcuate this hours state, no modification to last hour.
                # All modifications and related logic at the end of the hour.
                hour, tower_id, user_ids = entry.split(",")
                user_ids = user_ids.strip()
                users_this_hour += user_ids.split("|")
                current_state = set(user_ids.split("|"))
                network_state_new[tower_id] = current_state
                """
                previous_state = network_state[tower_id]
                transitions_added = new_state.difference(previous_state)
                transitions_removed = previous_state.difference(new_state)
                transitions_idle = new_state.intersection(previous_state)
                """
                # print "Added: ", transitions_added
                # print "Removed: ", transitions_removed
        print "Users in all towers(double counted):", len(users_this_hour)
        print "Users seen this hour: ", len(set(users_this_hour))
        print "States updated. Sending a few messages around."
        # Parse the .msg file
        print "Parsing: ", current_message_file
        with open(current_message_file) as data:
            for entry in data:
                # ID, TTL, Source, Destination, hop, trust
                id, ttl, src, dst, hop, trust = entry.strip().split(",")
                msg = Message(id, ttl, src, dst, hop, trust)
                message_queue[src].append(msg)
                dirty_nodes.append(src)
        if not first_state:
            for tower in network_state_new.keys():
                # Nodes that are new to a tower need to trigger msg exchanges, ignore this for first run
                # as the first run marks all of them as new!
                transitions_added = network_state_new[tower].difference(network_state_old[tower])
                dirty_nodes += transitions_added
        first_state = False
        print "Simulating message exchange on all nodes that belong to a network."
        for tower in network_state_new.keys():
            users_in_tower = network_state_new[tower]
            dirty = perform_message_exchanges(users_in_tower)
            if dirty:
                # print "Dirty node in this tower, adding all users!"
                dirty_nodes += users_in_tower # This list is gonna have a lot of repetitions, but it's OK.
        print "Updaing old state to new state."
        network_state_old = network_state_new

def perform_message_exchanges(users):
    global dirty_nodes
    dirty = False
    for u1 in users:
        if str(u1) in dirty_nodes:
            dirty = True
            for u2 in users:
                if u1 != u2:
                    # We have reached a state where message queue exchange needs to happen between u1 and u2
                    # Right now, we have no policy checks for this, need to check and use trust scores here.
                    mq12 = set(message_queue[u1] + message_queue[u2])
                    message_queue[u1] = message_queue[u2] = []
                    for m in mq12:
                        message_queue[u1].append(m)
                        message_queue[u2].append(m)
    return dirty

if __name__ == "__main__":
    main()

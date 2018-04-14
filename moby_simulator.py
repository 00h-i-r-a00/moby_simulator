#!/usr/bin/env python
from collections import defaultdict
import argparse
import sys

DATA_FILE_PREFIX = "data/"
CONFIG_FILE_PREFIX = "data/seeds/"
RESULT_FILE_PREFIX = "data/results/"
DATA_FILE_FORMAT = ".twr"
CONFIG_FILE_FORMAT = ".config"
RESULT_FILE_FORMAT = ".csv"

network_state_old = defaultdict(set)
network_state_new = defaultdict(set)
message_queue = defaultdict(dict)
message_queue_map = defaultdict(list)
message_delivered = defaultdict(list)
message_delivery_count = 0
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
    parser = argparse.ArgumentParser(description='Moby simulation script.')
    parser.add_argument('--configuration', help='Configuration to use for the simulation', type=int, nargs='?', default=0)
    args = parser.parse_args(sys.argv[1:])
    configuration = args.configuration
    print "Configuration file: ", configuration
    first_state = True
    total_messages = 0
    global dirty_nodes
    global message_delivery_count
    global network_state_new
    global network_state_old
    dirty_nodes = []
    configuration_file = CONFIG_FILE_PREFIX + str(configuration) + CONFIG_FILE_FORMAT
    result_file = RESULT_FILE_PREFIX + str(configuration) + RESULT_FILE_FORMAT
    # Parse the .config file
    print "Parsing configuration and messages from seed: ", configuration_file
    data = open(configuration_file)
    allusers, userpool = data.readline().strip().split(",")
    usermap = data.readline().strip()
    city_number = int(data.readline().strip())
    start_day = int(data.readline().strip())
    end_day = int(data.readline().strip())
    for entry in data:
        # print entry
        # ID, TTL, Source, Destination, hop, trust
        hour, id, ttl, src, dst, hop, trust = entry.strip().split(",")
        msg = Message(id, int(ttl), src, dst, hop, trust)
        message_queue_map[int(hour)].append(msg)
    for current_day in xrange(start_day, end_day):
        for current_hour in xrange(0,24):
            network_state_new = defaultdict(set)
            current_data_file = DATA_FILE_PREFIX + str(city_number) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
            users_this_hour = []
            if not first_state:
                print "Message Delivery count: ", message_delivery_count, " of: ", total_messages
                print "Delivery rate: ", (float(message_delivery_count) / total_messages)*100, "%"
            print "Processing hour: ", current_hour, " File: ", current_data_file
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
            message_hour = current_hour + (24 * (current_day - start_day))
            for msg in message_queue_map[message_hour]:
                message_queue[msg.src][msg.id] = msg
                dirty_nodes.append(msg.src)
                total_messages += 1
            users_this_hour = set(users_this_hour)
            print "Users seen this hour: ", len(users_this_hour)
            changes_added = changes_removed = []
            if not first_state:
                for tower in network_state_new.keys():
                    # Nodes that are new to a tower need to trigger msg exchanges, ignore this for first run
                    # as the first run marks all of them as new!
                    transitions_added = network_state_new[tower].difference(network_state_old[tower])
                    transitions_removed = network_state_old[tower].difference(network_state_new[tower])
                    changes_added += transitions_added
                    changes_removed += transitions_removed
                    dirty_nodes += transitions_added
            print "Network changes added: ", len(changes_added), " removed: ", len(changes_removed)
            print "Total dirty nodes: ", len(dirty_nodes)
            first_state = False
            print "Simulating message exchange on all nodes that belong to a network."
            for tower in network_state_new.keys():
                users_in_tower = network_state_new[tower]
                if perform_message_exchanges(users_in_tower):
                    dirty_nodes += users_in_tower
            print "Messages for this hour sent, message exchanges complete. Perform destination check"
            for user, mq in message_queue.iteritems():
                dellist = []
                for key, msg in mq.iteritems():
                    # print "Dst: ", msg.dst, "User:", user
                    if msg.id not in message_delivered[user]:
                        if msg.dst == user and msg.id:
                            message_delivery_count += 1
                            message_delivered[user].append(msg.id)
                            msg.ttl = 60
                        elif msg.ttl > 1:
                            msg.ttl -= 1
                        else:
                            dellist.append(msg.id)
                for id in dellist:
                    del message_queue[user][id]
            print "Updaing old state to new state."
            for key, value in network_state_new.iteritems():
                network_state_old[key] = value
            dirty_nodes = []
            with open(result_file, "a+") as out_file:
                dlim = ','
                out_file.write(getline(current_day, current_hour, len(users_this_hour), len(dirty_nodes), message_delivery_count, total_messages))
                out_file.write("\n")

def getline(*args):
    retstr = str(args[0])
    dlim = ','
    for i in args[1:]:
        retstr = retstr + dlim + str(i)
    return retstr

def clean_users(users):
    global dirty_nodes
    new_dirty = []
    for node in dirty_nodes:
        if node not in users:
            new_dirty.append(node)
    dirty_nodes = new_dirty

def perform_message_exchanges(users):
    dirty = list(set(users).intersection(dirty_nodes))
    for u1 in dirty:
        for u2 in users:
            if u1 == u2:
                continue
            mq1 = message_queue[u1]
            mq2 = message_queue[u2]
            for key in mq1.keys():
                mq2[key] = mq1[key]
            for key in mq2.keys():
                mq1[key] = mq2[key]
    return len(dirty) > 0
                    # Any of the trust score changing logic should come here.
    # print "Resulting message queue length: ", len(mq)

if __name__ == "__main__":
    main()

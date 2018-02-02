#!/usr/bin/env python
from collections import defaultdict

DATA_FILE_PREFIX = "data/0/"
DATA_FILE_FORMAT = ".twr"
MESSAGE_FILE_FORMAT = ".msg"

start_day = 0
end_day = 1
network_state_old = defaultdict(set)
network_state_new = defaultdict(set)
message_queue = defaultdict(list)
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
    first_state = True
    global dirty_nodes
    global message_delivery_count
    for current_day in xrange(start_day, end_day):
        for current_hour in xrange(0,24):
            dirty_nodes = []
            current_data_file = DATA_FILE_PREFIX + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
            current_message_file = DATA_FILE_PREFIX + str(current_day) + "_" + str(current_hour) + MESSAGE_FILE_FORMAT
            users_this_hour = []
            print "Message Delivery count: ", message_delivery_count
            print "Processing hour: ", current_hour
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
            print "Dirty nodes: ", dirty_nodes
            for tower in network_state_new.keys():
                users_in_tower = network_state_new[tower]
                temp_dirty_bit = False
                for user in users_in_tower:
                    if user in dirty_nodes:
                        temp_dirty_bit = True
                        break
                if temp_dirty_bit:
                    print "dirty bit, calling mx for tower ", tower, len(dirty_nodes), len(users_in_tower)
                    perform_message_exchanges(users_in_tower)
                    clean_users(users_in_tower)
            print "Messages for this hour sent, message exchanges complete. Perform destination check"
            for user, mq in message_queue.iteritems():
                new_mq = []
                for msg in mq:
                    # print "Dst: ", msg.dst, "User:", user
                    if msg.dst == user and msg.id not in message_delivered[user]:
                        message_delivery_count += 1
                        message_delivered[user].append(msg.id)
                        msg = Message(msg.id, int(msg.ttl)-60, msg.src, msg.dst, int(msg.hop)+1, msg.trust)
                    elif msg.ttl > 1:
                        msg = Message(msg.id, int(msg.ttl)-1, msg.src, msg.dst, int(msg.hop)+1, msg.trust)
                    new_mq.append(msg)
                message_queue[user] = new_mq
            print "Updaing old state to new state."
            network_state_old = network_state_new

def clean_users(users):
    global dirty_nodes
    new_dirty = []
    for node in dirty_nodes:
        if node not in users:
            new_dirty.append(node)
    dirty_nodes = new_dirty

def perform_message_exchanges(users):
    print "Exchange for: ", len(users)
    mq = []
    mqids = []
    for u in users:
        for m in message_queue[u]:
            if m.id not in mqids:
                mqids.append(m.id)
                mq.append(m)
    for u in users:
        message_queue[u] = mq
    print "Resulting message queue length: ", len(mq)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from collections import defaultdict
import argparse
import sys
import time
import pdb
import json

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
queue_occupancy = defaultdict(dict)
message_delays = defaultdict(int)
message_delivery_count = 0
dirty_nodes = []
total_message_exchanges = 0
total_time = 0

class Message:
    def __init__(self, id, ttl, src, dst, hop, trust):
        self.id  = id
        self.ttl = ttl
        self.src = src
        self.dst = dst
        self.hop = hop
        self.trust = trust

def main():
    global dirty_nodes
    global message_delivery_count
    global network_state_new
    global network_state_old
    parser = argparse.ArgumentParser(description='Moby simulation script.')
    parser.add_argument('--configuration', help='Configuration to use for the simulation', type=str, nargs='?', default=0)
    args = parser.parse_args(sys.argv[1:])
    configuration = args.configuration
    print("Configuration file: ", configuration)
    first_state = True
    total_messages1 = 0 #cumulative message uptil a particular hour
    total_messages2 = 0 #total messages inside the system
    configuration_file = CONFIG_FILE_PREFIX + str(configuration) + CONFIG_FILE_FORMAT
    result_file = RESULT_FILE_PREFIX + str(configuration) + RESULT_FILE_FORMAT
    result_file_queue_occupancy = RESULT_FILE_PREFIX + str(configuration) + '_queue_occupancy' + RESULT_FILE_FORMAT
    # Parse the .config file
    print("Parsing configuration and messages from seed: ", configuration_file)
    with open(configuration_file) as conffile:
        config = json.load(conffile)
    city_number = config["city"]
    start_day = config["start-day"]
    end_day = config["end-day"]
    seed = config["seed"]
    queue_size = config["queuesize"]
    numdays = end_day - start_day
    # adding these two just for the sake of consistency
    messagegenerationtype = config["messagegenerationtype"]
    deliveryratiotype = config["deliveryratiotype"] #1 == cumulative sum; #2 == total sum
    distributiontype = config["distributiontype"]
    threshold = config["threshold"]
    dos_number = config["dos-number"]
    jam_tower = config["jam-tower"]
    jam_tower_logic = config["jam-tower-logic"]
    jam_tower_list = config["jam-tower-list"]
    jam_user = config["jam-user"]
    jam_user_logic = config["jam-user-logic"]
    jam_user_set = set(config["jam-user-list"])
    messages = config["messages"]
    for message in messages:
        message_queue_map[message["hour"]].append(Message(
                message["id"],
                message["ttl"],
                message["src"],
                message["dst"],
                message["hour"],
                message["trust"]))
        total_messages2 += 1
    message_delay_file = RESULT_FILE_PREFIX + str(configuration) + '_message_delays.csv'
    for current_day in list(range(start_day, end_day)):
        for current_hour in list(range(0,24)):
            dirty_nodes = []
            network_state_new = defaultdict(set)
            if threshold == 0:
                current_data_file = DATA_FILE_PREFIX + str(city_number) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
            else:
                current_data_file = DATA_FILE_PREFIX + str(city_number) + "_" + str(threshold) + "/" + str(start_day) + "/" + str(numdays) + "/" + str(current_day) + "_" +              str(current_hour) + DATA_FILE_FORMAT
            users_this_hour = []
            if not first_state:
                total_messages = total_messages1 if deliveryratiotype == 1 else total_messages2
                print("Message Delivery count: ", message_delivery_count, " of: ", total_messages)
                print("Delivery rate: ", (float(message_delivery_count) / total_messages)*100, "%")
            print("Processing hour: ", current_hour, " File: ", current_data_file)
            with open(current_data_file) as data:
                for entry in data:
                    # Just calcuate this hours state, no modification to last hour.
                    # All modifications and related logic at the end of the hour.
                    hour, tower_id, user_ids = entry.split(",")
                    user_ids = user_ids.strip()
                    users_this_hour += user_ids.split("|")
                    current_state = set(user_ids.split("|"))
                    # Removing jammed users from network state.
                    current_state = current_state - jam_user_set
                    network_state_new[tower_id] = current_state
            print("Users in all towers(double counted):", len(users_this_hour))
            message_hour = current_hour + (24 * (current_day - start_day))
            for msg in message_queue_map[message_hour]:
                message_queue[msg.src][msg.id] = msg
                dirty_nodes.append(msg.src)
                total_messages1 += 1
            users_this_hour = set(users_this_hour)
            print("Users seen this hour: ", len(users_this_hour))
            changes_added = []
            changes_removed = []
            if not first_state:
                for tower in network_state_new.keys():
                    # Nodes that are new to a tower need to trigger msg exchanges, ignore this for first run
                    # as the first run marks all of them as new!
                    transitions_added = network_state_new[tower].difference(network_state_old[tower])
                    transitions_removed = network_state_old[tower].difference(network_state_new[tower])
                    changes_added += transitions_added
                    changes_removed += transitions_removed
                    dirty_nodes += transitions_added
            print("Network changes added: ", len(changes_added), " removed: ", len(changes_removed))
            print("Total dirty nodes: ", len(dirty_nodes))
            first_state = False
            print("Simulating message exchange on all nodes that belong to a network.")
            queue_occupancy[str(current_day) + "," + str(current_hour)] = defaultdict()
            # Remove jammed towers.
            for tower in jam_tower_list:
                network_state_new.pop(tower, None)
            message_exchange_handler(sorted(network_state_new.keys()), current_day, current_hour, dos_number, queue_size)
            for user, mq in message_queue.items():
                dellist = []
                for key, msg in mq.items():
                    # print "Dst: ", msg.dst, "User:", user
                    if msg.id not in message_delivered[user]:
                        if msg.dst == user and msg.id:
                            message_delivery_count += 1
                            message_delivered[user].append(msg.id)
                            if msg.id not in message_delays:
                                hour_of_simulation = ((current_day - start_day)*24) + current_hour
                                message_delays[msg.id] = int(hour_of_simulation - int(msg.hop))
                                print("Message delay: ", message_delays[msg.id])
                            msg.ttl = 60
                        elif msg.ttl > 1:
                            msg.ttl -= 1
                        else:
                            dellist.append(msg.id)
                for id in dellist:
                    del message_queue[user][id]
            for key, value in network_state_new.items():
                network_state_old[key] = value
            total_messages = total_messages1 if deliveryratiotype == 1 else total_messages2
            with open(result_file, "a+") as out_file:
                out_file.write(getline(current_day, current_hour, len(users_this_hour), len(dirty_nodes), message_delivery_count, total_messages))
    with open(result_file_queue_occupancy, "w") as outfile:
        for day in list(range(start_day, end_day)):
            for hour in list(range(0,24)):
                key = str(day) + "," + str(hour)
                for user, queueocc in queue_occupancy[key].items():
                    outfile.write(getline(key, user, queueocc))
    with open(message_delay_file, "w") as outfile:
        for user, msgids in message_delivered.items():
            for msgid in msgids:
                outfile.write(getline(msgid, message_delays[msgid]))
    print ("Simulation Done!")

def getline(*args):
    retstr = str(args[0])
    dlim = ','
    for i in args[1:]:
        retstr = retstr + dlim + str(i)
    retstr += '\n'
    return retstr

def perform_dos_exchanges(dos_number, tower, users_in_tower, current_day, current_hour):
    for i in list(range(0, dos_number)):
        id = str(tower) + "_" + str(current_day) + "_" + str(current_hour) + "_" + str(i)
        dos_message = Message(id, 100, -1, -1, -1, 0)
        for u in users_in_tower:
            message_queue[u][dos_message.id] = dos_message

def message_exchange_handler(network_towers, current_day, current_hour, dos_number, queue_size):
    global dirty_nodes
    global network_state_new
    saved_dirty_nodes = dirty_nodes
    for tower in network_towers:
        users_in_tower = network_state_new[tower]
        perform_dos_exchanges(dos_number, tower, users_in_tower, current_day, current_hour)
        if queue_size == 0:
            if perform_message_exchanges(users_in_tower, current_day, current_hour):
                dirty_nodes += users_in_tower
            else:
                pass
        else:
            if perform_message_exchanges_with_queue(users_in_tower, queue_size, current_day, current_hour):
                dirty_nodes += users_in_tower
            else:
                pass
    dirty_nodes = saved_dirty_nodes
    network_towers.reverse()
    for tower in network_towers:
        users_in_tower = network_state_new[tower]
        perform_dos_exchanges(dos_number, tower, users_in_tower, current_day, current_hour)
        if queue_size == 0:
            if perform_message_exchanges(users_in_tower, current_day, current_hour):
                dirty_nodes += users_in_tower
            else:
                pass
        else:
            if perform_message_exchanges_with_queue(users_in_tower, queue_size, current_day, current_hour):
                dirty_nodes += users_in_tower
            else:
                pass

def perform_message_exchanges(users, current_day, current_hour):
    queue_key = str(current_day) + "," + str(current_hour)
    dirty = list(set(users).intersection(dirty_nodes))
    if len(dirty) == 0:
        queue_occupancy[queue_key]['nouser'] = float('NaN')
        return False
    for u1 in dirty:
        for u2 in users:
            if u1 == u2:
                continue
            mq1 = message_queue[u1]
            mq2 = message_queue[u2]
            mq1.update(mq2)
            mq2.update(mq1)
            queue_occupancy[queue_key][u1] = len(mq1.keys())
            queue_occupancy[queue_key][u2] = len(mq2.keys())
    return True

def perform_message_exchanges_with_queue(users, queuesize, current_day, current_hour):
    queue_key = str(current_day) + "," + str(current_hour)
    dirty = list(set(users).intersection(dirty_nodes))
    if len(dirty) == 0:
        queue_occupancy[queue_key]['nouser'] = float('NaN')
    for u1 in dirty:
        for u2 in users:
            if u1 == u2:
                continue
            mq1 = message_queue[u1]
            mq2 = message_queue[u2]
            # In 1 but not 2
            mq12 = mq1.keys() - mq2.keys()
            # In 2 but not 1
            mq21 = mq2.keys() - mq1.keys()
            for key in mq12:
                if len(mq2.keys()) < queuesize:
                    mq2[key] = mq1[key]
                else:
                    break
            for key in mq21:
                if len(mq1.keys()) < queuesize:
                    mq1[key] = mq2[key]
                else:
                    break
            queue_occupancy[queue_key][u1] = len(mq1.keys())
            queue_occupancy[queue_key][u2] = len(mq2.keys())
    return len(dirty) > 0


if __name__ == "__main__":
    main()

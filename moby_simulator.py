#!/usr/bin/env python3
from collections import defaultdict
import argparse
from bitarray import bitarray
import json
import os
import pdb
import requests
import socket
import sys
import time
import tracemalloc

DATA_FILE_PREFIX = "data/"
CONFIG_FILE_PREFIX = "data/seeds/"
RESULT_FILE_PREFIX = "data/results/"
DATA_FILE_FORMAT = ".twr"
CONFIG_FILE_FORMAT = ".config"
RESULT_FILE_FORMAT = ".csv"

class Message:
    def __init__(self, id, ttl, src, dst, hour, trust):
        self.id  = id
        self.ttl = ttl
        self.src = src
        self.dst = dst
        self.hour = hour
        self.trust = trust

network_state_old = defaultdict(set)
network_state_new = defaultdict(set)
dead_user_map = {}
message_queue = {}
message_pool = []
queue_occupancy = defaultdict(dict)
dirty_nodes = set()
total_message_exchanges = 0
total_time = 0

def main():
    start = time.time()
    global dirty_nodes
    global network_state_new
    global network_state_old
    global queue_occupancy
    global message_pool
    global dead_user_map
    message_delays = defaultdict(int)
    parser = argparse.ArgumentParser(description='Moby simulation script.')
    parser.add_argument('--configuration', help='Configuration to use for the simulation', type=str, nargs='?', default=0)
    args = parser.parse_args(sys.argv[1:])
    configuration = args.configuration
    print("Configuration file: ", configuration)
    first_state = True
    total_messages = 0
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
    slack_hook = config["slack-hook"]
    dead_user_map = config["del-users"]
    message_pool = [None] * len(messages)
    userpool = config["userpool"]
    for u in userpool:
        message_queue[u] = bitarray(len(messages))
        message_queue[u].setall(0)
    message_delivered = bitarray(len(messages))
    message_delivered.setall(0)
    for message in messages:
        m = Message(int(message["id"]),
                int(message["ttl"]),
                message["src"],
                message["dst"],
                int(message["hour"]),
                float(message["trust"]))
        message_pool[m.id] = m
    message_delay_file = RESULT_FILE_PREFIX + str(configuration) + '_message_delays.csv'
    for current_day in list(range(start_day, end_day)):
        for current_hour in list(range(0,24)):
            tracemalloc.start()
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            print("TRACEMALLOC: ")
            for stat in top_stats[:10]:
                print(stat)
            dirty_nodes = set()
            network_state_new = defaultdict(set)
            if threshold == 0:
                current_data_file = DATA_FILE_PREFIX + str(city_number) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
            else:
                current_data_file = DATA_FILE_PREFIX + str(city_number) + "_" + str(threshold) + "/" + str(start_day) + "/" + str(numdays) + "/" + str(current_day) + "_" +              str(current_hour) + DATA_FILE_FORMAT
            users_this_hour = []
            if not first_state:
                print("Message Delivery count: ", message_delivered.count(), " of: ", total_messages)
                print("Delivery rate: ", (float(message_delivered.count()) / total_messages)*100, "%")
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
            users_this_hour = set(users_this_hour)
            message_hour = current_hour + (24 * (current_day - start_day))
            for msg in message_pool:
                if msg.hour == message_hour:
                    message_queue[msg.src][msg.id] = 1
                    dirty_nodes.add(msg.src)
                    total_messages += 1
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
                    dirty_nodes.update(set(transitions_added))
            print("Network changes added: ", len(changes_added), " removed: ", len(changes_removed))
            print("Total dirty nodes: ", len(dirty_nodes))
            first_state = False
            print("Simulating message exchange on all nodes that belong to a network.")
            queue_occupancy[str(current_day) + "," + str(current_hour)] = defaultdict()
            # Remove jammed towers.
            for tower in jam_tower_list:
                network_state_new.pop(tower, None)
            message_exchange_handler(sorted(network_state_new.keys()), current_day, current_hour, dos_number, queue_size)
            print("Done with msg exchange, destination checks.")
            for msgid in range(len(message_pool)):
                m = message_pool[msgid]
                if not message_delivered[msgid]:
                    try:
                        mq = message_queue[m.dst]
                    except KeyError:
                        continue
                    if mq[msgid]:
                        message_delivered[msgid] = 1
                        hour_of_simulation = ((current_day - start_day)*24) + current_hour
                        message_delays[msgid] = hour_of_simulation - m.hour
                        print("Message delay, ID: ", message_delays[msgid], msgid)
            for key, value in network_state_new.items():
                network_state_old[key] = value
            with open(result_file, "a+") as out_file:
                out_file.write(getline(current_day, current_hour, len(users_this_hour), len(dirty_nodes), message_delivered.count(), total_messages))
            delete_dead_users(message_hour)
    with open(result_file_queue_occupancy, "w") as outfile:
        for day in list(range(start_day, end_day)):
            for hour in list(range(0,24)):
                key = str(day) + "," + str(hour)
                for user, queueocc in queue_occupancy[key].items():
                    outfile.write(getline(key, user, queueocc))
    with open(message_delay_file, "w") as outfile:
        for msgid, delay in message_delays.items():
            outfile.write(getline(msgid, delay))
    time_taken = (time.time() - start) / 60
    print ("Simulation done in ", time_taken, "mins")
    # Handle slack hook
    if slack_hook != "":
        headers = {"Content-type": "application/json"}
        payload = {"text": "Simulation " + configuration + " done on " + socket.gethostname() + "!! Time taken: " + str(time_taken) + " mins."}
        try:
            requests.post(slack_hook, json=payload, headers=headers)
        except requests.exceptions.MissingSchema:
            print("Problem with posting to slack. Check hook URL!!")

def delete_dead_users(hour):
    dead_users = dead_user_map[str(hour)]
    print("Deleting user for hour:", hour, len(dead_users))
    for u in dead_users:
        del(message_queue[u])

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
                dirty_nodes.update(set(users_in_tower))
            else:
                pass
        else:
            if perform_message_exchanges_with_queue(users_in_tower, queue_size, current_day, current_hour):
                dirty_nodes.update(set(users_in_tower))
            else:
                pass
    dirty_nodes = saved_dirty_nodes
    network_towers.reverse()
    for tower in network_towers:
        users_in_tower = network_state_new[tower]
        perform_dos_exchanges(dos_number, tower, users_in_tower, current_day, current_hour)
        if queue_size == 0:
            if perform_message_exchanges(users_in_tower, current_day, current_hour):
                dirty_nodes.update(set(users_in_tower))
            else:
                pass
        else:
            if perform_message_exchanges_with_queue(users_in_tower, queue_size, current_day, current_hour):
                dirty_nodes.update(set(users_in_tower))
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
            b1 = message_queue[u1]
            b2 = message_queue[u2]
            message_queue[u1] |= b2
            message_queue[u2] |= b1
            queue_occupancy[queue_key][u1] = message_queue[u1].count()
            queue_occupancy[queue_key][u2] = message_queue[u2].count()
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

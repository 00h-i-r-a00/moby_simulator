#!/usr/bin/env python3
import sys, random, argparse
from collections import defaultdict
import pdb
import math
import numpy as np
import json
import os
import requests
import socket

DATA_FILE_PREFIX = "data/"
SEED_FILE_PREFIX = "data/seeds/"
DATA_FILE_FORMAT = ".twr"
CONFIGURATION_FILE_FORMAT = ".config"
COMMS_AGGREGATE_FILE_FORMAT = ".comagg"
COMMS_USER_FILE_FORMAT = ".comuser"
JSON = ".json"
message_id_start = DATA_FILE_PREFIX
overall_network_state = defaultdict(dict)
tower_population = defaultdict(int)
towers_seen = defaultdict(bool)
user_mobility = defaultdict(list)
def main():
    userpool = defaultdict(int)
    users_to_consider = defaultdict(set)
    active_userpool_per_hour = {}
    del_users = {}
    parser = argparse.ArgumentParser(description='Moby message generation script script.')
    parser.add_argument('--start-day', help='start day of the year', type=int, nargs='?', default=53)
    parser.add_argument('--end-day', help='end day of the year', type=int, nargs='?', default=56)
    parser.add_argument('--city-number', help='City to generate messages for', type=int, nargs='?', default=0)
    parser.add_argument('--seed', help='Number to use for random seeding', type=int, nargs='?', default=3007052)
    parser.add_argument('--attack-user', help='Number of users to compromise.', type=int, nargs='?', default=0)
    parser.add_argument('--attack-logic', help='Choose whether to jam randomly, or based on len of contacts', type=int, nargs='?', default=0)
    parser.add_argument('--trust-scores', help='Trust score file to be used.', type=str, nargs='?', default="")
    args = parser.parse_args(sys.argv[1:])
    start_day = args.start_day
    end_day = args.end_day
    if end_day is None:
        end_day = start_day + 3
    city = args.city_number
    seed = args.seed
    compromise_number = args.attack_user
    attack_logic = args.attack_logic
    trust_scores = args.trust_scores
    total_hours = (end_day - start_day) * 24
    print("Loading trust score mappings...")
    score_sets = {}
    with open(DATA_FILE_PREFIX + trust_scores + JSON) as infile:
        for d in json.load(infile)["users"]:
                for k, v in d.items():
                    score_sets[int(k)] = set([int(i) for i in v])
                    score_sets[int(k)] = score_sets[int(k)] - set([int(k)])
    print("Loaded", len(score_sets), "trust scores...")
    print("Compromise number:", compromise_number)
    print("Seed:", seed)
    random.seed(seed)
    if compromise_number > 0:
        print("Generating list for compromise users...")
        if attack_logic == 0:
            tmp_lst = sorted(score_sets.keys())
            random.shuffle(tmp_lst)
            compromised_users = set(tmp_lst[:compromise_number])
        elif attack_logic == 1:
            compromised_users = set([i for i in sorted(score_sets, key=lambda k: len(score_sets[k]), reverse=True)][:compromise_number])
    print(len(compromised_users), hash(tuple(compromised_users)))
    h = 0
    print("Generating userpool...")
    for current_day in range(start_day, end_day):
        for current_hour in range(0,24):
            current_data_file = DATA_FILE_PREFIX + str(city) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
            users_this_hour = []
            with open(current_data_file) as data:
                for entry in data:
                    hour, tower_id, user_ids = entry.split(",")
                    user_ids = user_ids.strip()
                    users_this_hour += user_ids.split("|")
                    overall_network_state[h][tower_id] = set([int(i) for i in user_ids.split("|")])
            users_this_hour = set(users_this_hour)
            for j in range(0, h):
                users_to_consider[j] = users_to_consider[j].union(users_this_hour)
            active_userpool_per_hour[h] = users_this_hour
            h += 1
            for u in users_this_hour:
                userpool[u] += 1
    print("Active userpool per hour len", len(active_userpool_per_hour))
    print("Total users seen: ", len(userpool))
    allusers = dict(userpool)
    filtered_users = set(userpool.keys())
    users_in_pool = sorted(list(userpool.keys()))
    print("Checking extent of compromise...")
    output = {}
    h = 0
    tmx_tracker = defaultdict(int)
    for current_day in range(start_day, end_day):
        for current_hour in range(0, 24):
            compromised = 0
            userctr = 0
            new_compromised = set()
            missed_trust = 0
            missed_trust_2 = 0
            tmx = 0
            users_hour = 0
            mx = 0
            ulen_lst = []
            save = {}
            compr_ctr = 0
            len_new_compr = 0
            for tower_id, users in overall_network_state[h].items():
                ulen = len(users)
                ulen_lst.append(ulen)
                userctr += ulen
                mx += (ulen - 1) * (ulen - 2)
                for u in users:
                    users_hour += 1
                    try:
                        trusted_mx = len(score_sets[u].intersection(users))
                        tmx += trusted_mx
                        if trusted_mx > 0:
                            tmx_tracker[u] += trusted_mx
                    except KeyError:
                        missed_trust += 1
                for u in users.intersection(compromised_users):
                    compr_ctr += 1
                    try:
                        new_compromised = new_compromised.union(users.intersection(score_sets[u]))
                        len_new_compr += len(users.intersection(score_sets[u]))
                    except KeyError:
                        missed_trust_2 += 1
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("TMX Tracker:", len(tmx_tracker.keys()))
            print("Overlap:", len(set(tmx_tracker.keys()).intersection(compromised_users)))
            print("Towers this hour:", len(overall_network_state[h]))
            print("Users seen this hour:", users_hour)
            print("Trusted MX:", tmx)
            print("Missed trust for", missed_trust, "and", missed_trust_2, "this hour...")
            print("Seen compromised:", compr_ctr, "len new compromised", len_new_compr)
            print("Compromised this hour:", len(new_compromised), "of", userctr, ". Updating set...")
            compromised_users = compromised_users.union(new_compromised)
            print("Size of new compromised set:", len(compromised_users))
            save["mx"] = mx
            save["tmx"] = tmx
            save["towers"] = len(ulen_lst)
            save["users"] = userctr
            save["min_users"] = min(ulen_lst)
            save["max_users"] = max(ulen_lst)
            save["avg_users"] = round(userctr / len(ulen_lst), 2)
            output[h] = save
            h += 1
    print("Extent of compromise:", len(compromised_users)/len(users_in_pool), len(compromised_users), "of", len(users_in_pool))
    print("Hour, Towers, Users, Min users, Max users, Avg users, Message exchanges, Trusted exchanges")
    for h, save in output.items():
        print(getline(h, save["towers"], save["users"], save["min_users"], save["max_users"], save["avg_users"], save["mx"], save["tmx"]))

def getline(*args):
    retstr = str(args[0])
    dlim = ','
    for i in args[1:]:
        retstr = retstr + dlim + str(i)
    return retstr

if __name__ == "__main__":
    main()

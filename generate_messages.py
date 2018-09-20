#!/usr/bin/env python3
import sys, random, argparse
from collections import defaultdict
import pdb
import math
import numpy as np
import os
import json

DATA_FILE_PREFIX = "data/"
SEED_FILE_PREFIX = "data/seeds/"
DATA_FILE_FORMAT = ".twr"
CONFIGURATION_FILE_FORMAT = ".config"
COMMS_AGGREGATE_FILE_FORMAT = ".comagg"
COMMS_USER_FILE_FORMAT = ".comuser"
message_id_start = DATA_FILE_PREFIX
overall_network_state = defaultdict(dict)
tower_population = defaultdict(int)
towers_seen = defaultdict(bool)
user_mobility = defaultdict(list)
def main():
    userpool = defaultdict(int)
    active_userpool_per_hour = {}
    parser = argparse.ArgumentParser(description='Moby message generation script script.')
    parser.add_argument('--number', help='Number of messages to generate', type=int, nargs='?', default=1000)
    parser.add_argument('--start-day', help='start day of the year', type=int, nargs='?', default=0)
    parser.add_argument('--end-day', help='end day of the year', type=int, nargs='?', default=None)
    parser.add_argument('--configuration', help='Configuration and message file id', type=str, nargs='?', default=0)
    parser.add_argument('--city-number', help='City to generate messages for', type=int, nargs='?', default=0)
    parser.add_argument('--threshold', help='Minimum occourances to be considered a legit user', type=int, nargs='?', default=0)
    parser.add_argument('--cooldown', help='Cooldown hours, messages distributed over total hours - cooldown hours.', type=int, nargs='?', default=12)
    parser.add_argument('--ttl', help='The time to live to be used for the messages', type=int, nargs='?', default=72)
    parser.add_argument('--seed', help='Number to use for random seeding', type=int, nargs='?', default=3007052)
    parser.add_argument('--queuesize', help='0 if no queuesize else a specific number with the queuesize value', type=int, nargs='?', default=0)
    parser.add_argument('--deliveryratiotype', help='1 if total_messages == upto that hour; 2 if total_messages == total number of messages in all hours', type=int, nargs='?', default=1)
    parser.add_argument('--messagegenerationtype', help='Original Criteria or Selectively changing sources and destinations', type=int, nargs='?', default=1)
    parser.add_argument('--distributiontype', help='2 types -> "uniform" or "user-activity-based" ; used in conjunction with messagegenerationtype', type=str, nargs='?', default='uniform')
    parser.add_argument('--dos-number', help='Number of dos messages to send at each tower.', type=int, nargs='?', default=0)
    parser.add_argument('--jam-tower', help='Number of towers to jam.', type=int, nargs='?', default=0)
    parser.add_argument('--jam-tower-logic', help='The logic used to pick towers to jam.', type=int, nargs='?', default=0)
    parser.add_argument('--jam-user', help='Number of users to jam.', type=int, nargs='?', default=0)
    parser.add_argument('--jam-user-logic', help='The logic used to pick users to jam.', type=int, nargs='?', default=0)
    args = parser.parse_args(sys.argv[1:])
    number_of_messages = args.number
    start_day = args.start_day
    end_day = args.end_day
    if end_day is None:
        end_day = start_day + 3
    configuration = args.configuration
    city = args.city_number
    cooldown =  args.cooldown
    threshold = args.threshold
    time_to_live = args.ttl
    seed = args.seed
    queuesize = args.queuesize
    message_generation_type = args.messagegenerationtype
    deliveryratiotype = args.deliveryratiotype
    distributiontype = args.distributiontype
    dos_number = args.dos_number
    jam_tower = args.jam_tower
    jam_tower_logic = args.jam_tower_logic
    jam_tower_list = []
    jam_user = args.jam_user
    jam_user_logic = args.jam_user_logic
    jam_user_list = []
    message_sending_hours = ((end_day - start_day) * 24) - cooldown
    h = 0
    print(message_sending_hours)
    for current_day in range(start_day, end_day):
        for current_hour in range(0,24):
            current_data_file = DATA_FILE_PREFIX + str(city) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
            users_this_hour = []
            with open(current_data_file) as data:
                for entry in data:
                    hour, tower_id, user_ids = entry.split(",")
                    user_ids = user_ids.strip()
                    users_this_hour += user_ids.split("|")
                    overall_network_state[h][tower_id] = len(set(user_ids.split("|")))
                    # Only need this under that specific scenario.
                    towers_seen[tower_id] = True
                    if jam_tower_logic == 1:
                        tower_population[tower_id] += len(user_ids)
                    # Expensive operation, only perform if it's that case.
                    if jam_user_logic == 2:
                        for u in users_this_hour:
                            user_mobility[u].append(tower_id)
            users_this_hour = set(users_this_hour)
            active_userpool_per_hour[h] = users_this_hour
            h += 1
            for u in users_this_hour:
                userpool[u] += 1
    print("Total users seen: ", len(userpool))
    allusers = dict(userpool)
    #faster method to delete
    userpool = dict((k, v) for (k, v) in userpool.items() if v >= threshold)
    print("Users above threshold: ", len(userpool), " percentage: ", (float(len(userpool))/float(len(allusers)) * 100), "%")
    users_in_pool = list(userpool.keys())
    current_message_file = SEED_FILE_PREFIX + str(configuration) + CONFIGURATION_FILE_FORMAT
    config = {}
    config["alluserslen"] = len(allusers)
    config["userpoollen"] = len(userpool)
    # Dropping writing user pool, not really used, only there for possible need to debug.
    # config["userpool"] = users_in_pool
    config["city"] = city
    config["start-day"] = start_day
    config["end-day"] = end_day
    config["seed"] = seed
    config["queuesize"] = queuesize
    config["messagegenerationtype"] = message_generation_type
    config["deliveryratiotype"] = deliveryratiotype
    config["distributiontype"] = distributiontype
    config["threshold"] = threshold
    config["dos-number"] = dos_number
    config["jam-tower"] = jam_tower
    config["jam-tower-logic"] = jam_tower_logic
    random.seed(seed)
    if jam_tower > 0:
        print("Generating jammed towers list.")
        if jam_tower_logic == 0:
            print("Logic for tower jamming: Random. Jamming", jam_tower,"towers.")
            jam_tower_list = random.sample(towers_seen.keys(), jam_tower)
        elif jam_tower_logic == 1:
            print("Logic for tower jamming: Population oracle. Jamming", jam_tower, "towers.")
            jam_tower_list = [tower for tower in sorted(tower_population, key=tower_population.get, reverse=True)][:jam_tower]
    config["jam-tower-list"] = jam_tower_list
    config["jam-user"] = jam_user
    config["jam-user-logic"] = jam_user_logic
    random.seed(seed)
    if jam_user > 0:
        print("Generating jammed user set.")
        if jam_user_logic == 0:
            print("Logic for user jamming: Random. Jamming", jam_user, "users.")
            jam_user_list = random.sample(users_in_pool, jam_user)
        elif jam_tower_logic == 1:
            print("Logic for user jamming: Popularity oracle. Jamming", jam_user, "users.")
            # TODO: Parse popularity from comms files.
        elif jam_tower_logic == 2:
            print("Logic for user jamming: Mobility oracle. Jamming", jam_user, "users.")
            for u in user_mobility.keys():
                user_mobility[u] = len(set(user[u]))
            jam_user_list = [user for user in sorted(user_mobility, key=user_mobility.get, reverse=True)][:jam_user]
    config["jam-user-list"] = jam_user_list
    print("Configuration without messages: ", config)
    print("Generating messages for config message file", current_message_file)
    distribution = get_message_distribution(message_sending_hours, number_of_messages, distributiontype, start_day, end_day, city, users_in_pool)
    print(distribution)
    # Reseeding for message generation to comply with previously run simulations.
    random.seed(seed)
    messages = []
    userpool_keys = sorted(userpool.keys())
    for hour in range(message_sending_hours):
        message_number = distribution[hour]
        for i in range(int(math.ceil(message_number))):
            message = {}
            message["hour"] = hour
            message["id"] = DATA_FILE_PREFIX + str(hour) + "_" + str(i)
            # Don't use the message_generation_type flag for now, maybe need it in the future.
            # if message_generation_type == 1:
            src, dst = random.sample(userpool_keys, 2)
            message["src"] = src
            message["dst"] = dst
            message["ttl"] = 72
            message["hop"] = 0
            message["trust"] = 1
            messages.append(message)
    config["messages"] = messages
    with open(current_message_file, "w+") as outfile:
        json.dump(config, outfile)
    print("Message generation complete and written to file:", current_message_file)

def get_message_distribution(sending_hours, total_messages, dist_type, start, end, city, users):
    dictionary = {}
    # Uniform distrbution for now.
    if dist_type == 'uniform':

        overflow = total_messages % sending_hours

        for i in range(0, sending_hours):
            dictionary[i] = int(total_messages / sending_hours)
        for i in range(0, overflow):
            dictionary[i] += 1
        return dictionary

    elif dist_type == 'region_sms_based':
        smscounter = defaultdict(int)
        smstotal = 0
        tot = 0
        for day in range(start, end):
            commsfile = DATA_FILE_PREFIX + str(city) + "/" + str(day) + COMMS_AGGREGATE_FILE_FORMAT
            with open(commsfile) as data:
                for entry in data:
                    hour, towernum, usernum, callnum, smsnum = entry.split(",")
                    current_hour = ((day - start) * 24) + int(hour)
                    if current_hour > sending_hours:
                        break
                    else:
                        smscounter[current_hour] = int(smsnum.strip())
                        smstotal += int(smsnum.strip())
        # If this gives a Key Error, there's something wrong with the data.
        for i in range(0, sending_hours):
            scaling = float(smscounter[i]) / smstotal
            dictionary[i] = int(math.ceil(scaling * total_messages))
            tot += dictionary[i]
        print("Total messages:", tot)
        return dictionary

    elif dist_type == 'user_sms_based':
        smscounter = defaultdict(int)
        smstotal = 0
        tot = 0
        for day in range(start, end):
            commsfile = DATA_FILE_PREFIX + str(city) + "/" + str(day) + COMMS_USER_FILE_FORMAT
            with open(commsfile) as data:
                for entry in data:
                    hour, user, callnum, smsnum = entry.split(",")
                    current_hour = ((day - start) * 24) + int(hour)
                    if current_hour > sending_hours:
                        break
                    else:
                        if user.strip() in users:
                            smscounter[current_hour] += int(smsnum.strip())
                            smstotal += int(smsnum.strip())
        for i in range(0, sending_hours):
            scaling = float(smscounter[i]) / smstotal
            dictionary[i] = int(math.ceil(scaling * total_messages))
            tot += dictionary[i]
        print("Total Messages:", tot)
        return dictionary

    elif dist_type == 'user_activity_based':
        medians = {}
        h = 0
        total = 0
        total_msgs_sent = 0
        for i in range(0, sending_hours):
            users = []
            for tower, num_users in overall_network_state[i].items():
                users.append(num_users)

            medians[i] = np.median(users)
            total += medians[i]

        total_msgs_sent = 0

        for i in range(0, sending_hours):

             dictionary[i] = int(math.ceil((medians[i]/total) * total_messages))
             total_msgs_sent += dictionary[i]

        overflow = total_messages - total_msgs_sent

        for i in range(0, overflow):
            dictionary[i] += 1
        return dictionary

    elif dist_type == 'total_users_based':

        total_users = 0
        users_per_hour = {}
        total_msgs_sent = 0

        for i in range(0, sending_hours):
            users_sum = 0
            for tower, num_users in overall_network_state[i].items():
                users_sum += num_users

            total_users += users_sum

            users_per_hour[i] = users_sum

        for i in range(0, sending_hours):
            dictionary[i] = int(math.ceil((users_per_hour[i]/total_users) * total_messages))
            total_msgs_sent += dictionary[i]

        overflow = total_messages - total_msgs_sent


        for i in range(0, overflow):
            dictionary[i] += 1

        return dictionary

if __name__ == "__main__":
    main()

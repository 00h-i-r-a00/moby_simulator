#!/usr/bin/env python
from __future__ import division
import sys, random, argparse
from collections import defaultdict
import pdb
import math
import numpy as np
import os

DATA_FILE_PREFIX = "data/"
SEED_FILE_PREFIX = "data/seeds/"
DATA_FILE_FORMAT = ".twr"
CONFIGURATION_FILE_FORMAT = ".config"
message_id_start = DATA_FILE_PREFIX
overall_network_state = defaultdict(dict)
def main():
    userpool = defaultdict(int)	
    active_userpool_per_hour = {}
    parser = argparse.ArgumentParser(description='Moby message generation script script.')
    parser.add_argument('--number', help='Number of messages to generate', type=int, nargs='?', default=1000)
    parser.add_argument('--start-day', help='start day of the year', type=int, nargs='?', default=0)
    parser.add_argument('--end-day', help='end day of the year', type=int, nargs='?', default=None)
    parser.add_argument('--configuration', help='Configuration and message file id', type=str, nargs='?', default=0)
    parser.add_argument('--city-number', help='City to generate messages for', type=int, nargs='?', default=0)
    parser.add_argument('--threshold', help='Minimum occourances to be considered a legit user', type=int, nargs='?', default=24)
    parser.add_argument('--cooldown', help='Cooldown hours, messages distributed over total hours - cooldown hours.', type=int, nargs='?', default=12)
    parser.add_argument('--ttl', help='The time to live to be used for the messages', type=int, nargs='?', default=72)
    parser.add_argument('--seed', help='Number to use for random seeding', type=int, nargs='?', default=3007052)
    parser.add_argument('--queuesize', help='0 if no queuesize else a specific number with the queuesize value', type=int, nargs='?', default=0)
    parser.add_argument('--percentagehoursactive', help='Percentage of hours the destinations stay active', type=int, nargs='?', default=100)
    parser.add_argument('--deliveryratiotype', help='1 if total_messages == upto that hour; 2 if total_messages == total number of messages in all hours', type=int, nargs='?', default=1)
    parser.add_argument('--messagegenerationtype', help='Original Criteria or Selectively changing sources and destinations', type=int, nargs='?', default=1)
    parser.add_argument('--distributiontype', help='2 types -> "uniform" or "user-activity-based" ; used in conjunction with messagegenerationtype', type=str, nargs='?', default='uniform')
    parser.add_argument('--sybil-number', help='Number of sybil messages to send at each tower.', type=int, nargs='?', default=0)
    parser.add_argument('--usethreshold', help='Use this flag if you want to run the simulation based on the reduced threshold defined user-set', action='store_true')
    
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
    percentage_hours_active = args.percentagehoursactive
    message_generation_type = args.messagegenerationtype
    deliveryratiotype = args.deliveryratiotype
    distributiontype = args.distributiontype
    sybil_number = args.sybil_number
	usethreshold = args.usethreshold
	
    message_sending_hours = ((end_day - start_day) * 24) - cooldown


    h = 0
    print message_sending_hours
    print "Configuration (configuration, start, end, number, city, threshold, sending hours): ", configuration, start_day, end_day, number_of_messages, city, threshold, message_sending_hours

    for current_day in xrange(start_day, end_day):
        for current_hour in xrange(0,24):
            current_data_file = DATA_FILE_PREFIX + str(city) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
            users_this_hour = []
            with open(current_data_file) as data:
                for entry in data:
                    hour, tower_id, user_ids = entry.split(",")
                    user_ids = user_ids.strip()
                    users_this_hour += user_ids.split("|")
                    overall_network_state[h][tower_id] = len(set(user_ids.split("|")))
            users_this_hour = set(users_this_hour)
            active_userpool_per_hour[h] = users_this_hour

            h += 1

            for u in users_this_hour:
                userpool[u] += 1
    dellist = []
    for key, value in userpool.iteritems():
        if value < threshold:
            dellist.append(key)
    print "Total users seen: ", len(userpool)
    allusers = dict(userpool)
    for u in dellist:
        del userpool[u]
    print "Users above threshold: ", len(userpool), " percentage: ", (float(len(userpool))/float(len(allusers)) * 100), "%"
    users_in_pool = userpool.keys()
    current_message_file = SEED_FILE_PREFIX + str(configuration) + CONFIGURATION_FILE_FORMAT
# CONFIG FILE FORMAT:
# length of all users, length of user pool
# All users, comma seperated.
# City number
# Start day
# End day
# Seed

#########create threshold specific data folders###################################
    foldername = DATA_FILE_PREFIX + str(city) + "_" + str(threshold)
    
    if not os.path.exists(os.getcwd() + "/" + foldername):
        
        os.makedirs(os.getcwd() + "/" + foldername)
        for current_day in xrange(start_day, end_day):
            for current_hour in xrange(0,24):
  
                current_output_data_file = foldername + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
                thresh_out = open(current_output_data_file, 'w')
                current_data_file = DATA_FILE_PREFIX + str(city) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
                users_this_hour = []
                print "Filtering Users : hour %d , day %d " %(current_hour, current_day)
                with open(current_data_file) as data:
                    for entry in data:
                        hour, tower_id, user_ids = entry.split(",")
                        user_ids = user_ids.strip().split("|")
                        threshold_users_per_tower = [user for user in user_ids if user in users_in_pool]
                    
                        if len(threshold_users_per_tower) != 0:
                            out_row = hour + "," + tower_id + "," + "|".join(threshold_users_per_tower) 
                            thresh_out.write(out_row + "\n")
                    
                thresh_out.close()
    else:
        print "Folder for the threshold already exists"                
      
####################################################################################

    with open(current_message_file, "w+") as out_file:
        out_file.write(str(len(allusers)) + "," + str(len(userpool)))
        out_file.write("\n")
        for u in userpool.iterkeys():
            out_file.write("," + u)
        out_file.write("\n")
        out_file.write(str(city) + "\n")
        out_file.write(str(start_day) + "\n")
        out_file.write(str(end_day) + "\n")
        out_file.write(str(seed) + "\n")
        out_file.write(str(queuesize) + "\n")
        out_file.write(str(percentage_hours_active) + "\n")
        out_file.write(str(message_generation_type) + "\n")
        out_file.write(str(deliveryratiotype) + "\n")
        out_file.write(str(distributiontype) + "\n")
        out_file.write(str(threshold) + "\n")
        out_file.write(str(sybil_number) + "\n")
		out_file.write(str(usethreshold) + "\n")
		
    print "Generating: ", current_message_file
    distribution = get_message_distribution(message_sending_hours, number_of_messages, distributiontype)
    # ID, TTL, Source, Destination, hop, trust
    random.seed(seed)

    for hour in xrange(message_sending_hours):
        message_number = distribution[hour]
        sources_pool = active_userpool_per_hour[hour]
        destinations_pool = get_destinations_active_for_X_percentage_of_hours(percentage_hours_active, active_userpool_per_hour, hour)

        with open(current_message_file, "a+") as out_file:

            for i in xrange(int(math.ceil(message_number))):

                id = DATA_FILE_PREFIX + str(hour) + "_" + str(i)

                if message_generation_type == 1:
                    src, dst = random.sample(userpool.keys(), 2)
                    print "Msg No: %d, Current hour %d --> Sources Pool Size: %d ; Destinations Pool Size: %d for threshold %d" % (i, hour, len(userpool), len(userpool), threshold)
                elif message_generation_type == 2:
                    src, dst = random.sample(sources_pool, 1)[0], random.sample(destinations_pool, 1)[0]

                    print "Msg No:: %d, Current hour % d --> Sources Pool Size: %d ; Destinations Pool Size: %d" % (i, hour, len(sources_pool), len(destinations_pool))

                src = str(src)
                dst = str(dst)
                ttl = "72"
                hop = "0"
                trust = "1"
                out_file.write(getline(hour, id, ttl, src, dst, hop, trust))
                out_file.write("\n")

def get_message_distribution(sending_hours, total_messages, dist_type):
    dictionary = {}
    # Uniform distrbution for now.
    if dist_type == 'uniform':

        overflow = total_messages % sending_hours

        for i in xrange(0, sending_hours):
            dictionary[i] = total_messages / sending_hours
        for i in xrange(0, overflow):
            dictionary[i] += 1
        return dictionary

    elif dist_type == 'user_activity_based':
        medians = {}
        h = 0
        total = 0
        total_msgs_sent = 0
        for i in xrange(0, sending_hours):
            users = []
            for tower, num_users in overall_network_state[i].iteritems():
                users.append(num_users)

            medians[i] = np.median(users)
            total += medians[i]

        total_msgs_sent = 0

        for i in xrange(0, sending_hours):

             dictionary[i] = int(math.ceil((medians[i]/total) * total_messages))
             total_msgs_sent += dictionary[i]

        overflow = total_messages - total_msgs_sent

        for i in xrange(0, overflow):
            dictionary[i] += 1
        return dictionary

    elif dist_type == 'total_users_based':

        total_users = 0
        users_per_hour = {}
        total_msgs_sent = 0

        for i in xrange(0, sending_hours):
            users_sum = 0
            for tower, num_users in overall_network_state[i].iteritems():
                users_sum += num_users

            total_users += users_sum

            users_per_hour[i] = users_sum

        for i in xrange(0, sending_hours):
            dictionary[i] = int(math.ceil((users_per_hour[i]/total_users) * total_messages))
            total_msgs_sent += dictionary[i]

        overflow = total_messages - total_msgs_sent


        for i in xrange(0, overflow):
            dictionary[i] += 1

        return dictionary

def get_destinations_active_for_X_percentage_of_hours(x, active_user_pool_per_hour, current_hour):

    destinations_pool = []
    destinations_active = defaultdict(int)

    ##checking the number of hours the destinations are active beyond the current hour

    for hour in xrange(current_hour, len(active_user_pool_per_hour.keys())):

        for user in active_user_pool_per_hour[hour]:
            destinations_active[user] += 1

    total_hours_remaining = len(active_user_pool_per_hour.keys()) - current_hour

    for user, occurences in destinations_active.iteritems():
        active_percentage = (occurences/total_hours_remaining)*100

        if active_percentage >= x:
            destinations_pool.append(user)
   # destinations_pool = destinations_active.keys()


    return destinations_pool

def getline(*args):
    retstr = str(args[0])
    dlim = ','
    for i in args[1:]:
        retstr = retstr + dlim + str(i)
    return retstr

if __name__ == "__main__":
    main()

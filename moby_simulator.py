#!/usr/bin/env python3
from collections import defaultdict
import argparse
import sys
import time
import pdb
import msgpack
import queue
##from asyncio import PriorityQueue
#1. generate data based on queues -> run generate_messages.py
#2. test moby_simulator on that data

DATA_FILE_PREFIX = "/home/hiraj/moby_simulator/data/"
CONFIG_FILE_PREFIX = "/home/hiraj/moby_simulator/data/seeds/"
RESULT_FILE_PREFIX = "/home/hiraj/moby_simulator/data/results/"
DATA_FILE_FORMAT = ".twr"
CONFIG_FILE_FORMAT = ".config"
RESULT_FILE_FORMAT = ".csv"

network_state_old = defaultdict(set)
network_state_new = defaultdict(set)
#now the message_queue is a dictionary of type message_queue[user][msg.id][trust/prio]
#at the moment there are only two priorities
message_queue = defaultdict(dict)
message_queue_map = defaultdict(list)
message_delivered = defaultdict(list)
queue_occupancy = defaultdict(dict)
message_delays = defaultdict(int)
message_delivery_count = 0
dirty_nodes = []
total_message_exchanges = 0
total_time = 0
trust_scores = {}
#deletion is going to take the worse-case time of O(n); different than a dictionary where you can do it in O(1) time

#TODO: modify the function

def deleteMsgFromQueue(msg_queue, msgid):
	pass
	#del msg_queue[msgid] 
	# ~ for index, msg_ in enumerate(msg_queue.queue):
		# ~ msg = msg_[1]
		# ~ if msg.id == msgid:
			# ~ msg_queue.queue.pop(index)

class Message:
	def __init__(self, id, ttl, src, dst, hop, trust):
		self.id  = id
		self.ttl = ttl
		self.src = src
		self.dst = dst
		self.hop = hop
		self.trust = trust

		#TODO:Do I need these two comparators since I am not comparing the priority of two msg classes anymore?
	def __cmp__(self, other):
		return cmp(self.trust, other.trust)

	def __lt__(self, other):
		selfPriority = self.trust
		otherPriority = other.trust
		return selfPriority < otherPriority

def main():

	parser = argparse.ArgumentParser(description='Moby simulation script.')
	parser.add_argument('--configuration', help='Configuration to use for the simulation', type=str, nargs='?', default=0)

	args = parser.parse_args(sys.argv[1:])
	configuration = args.configuration
	print("Configuration file: ", configuration)
	first_state = True
	total_messages1 = 0 #cumulative message uptil a particular hour
	total_messages2 = 0 #total messages inside the system

	global dirty_nodes
	global message_delivery_count
	global network_state_new
	global network_state_old
	global trust_scores
	dirty_nodes = []

	configuration_file = CONFIG_FILE_PREFIX + str(configuration) + CONFIG_FILE_FORMAT

	result_file = RESULT_FILE_PREFIX + str(configuration) + RESULT_FILE_FORMAT
	result_file_queue_occupancy = RESULT_FILE_PREFIX + str(configuration) + '_queue_occupancy' + RESULT_FILE_FORMAT

	# Parse the .config file
	print("Parsing configuration and messages from seed: ", configuration_file)
	data = open(configuration_file)
	allusers, userpool = data.readline().strip().split(",")
	usermap = data.readline().strip()
	city_number = int(data.readline().strip())
	start_day = int(data.readline().strip())
	end_day = int(data.readline().strip())
	seed = int(data.readline().strip())
	queuesize = int(data.readline().strip())

#adding these two just for the sake of consistency


	percentagehoursactive = int(data.readline().strip())
	messagegenerationtype = int(data.readline().strip())
	deliveryratiotype = int(data.readline().strip()) #1 == cumulative sum; #2 == total sum
	distributiontype = str(data.readline().strip())
	threshold = str(data.readline().strip())
	sybil_number = int(data.readline().strip())
	trust_scores_file = data.readline().strip()
	message_delay_file = CONFIG_FILE_PREFIX + str(configuration) + '_message_delays.csv'
	file_delay = open(message_delay_file, 'w')


	##getting trust scores###

	print("Loading trust scores file %s" % trust_scores_file)
	with open(trust_scores_file, 'rb') as fm:
		trust_scores = msgpack.load(fm)


	for entry in data:
		# print entry
		# ID, TTL, Source, Destination, hop, trust
		hour, id, ttl, src, dst, hop, trust = entry.strip().split(",")
		msg = Message(id, int(ttl), src, dst, int(hour), int(trust))
		# Hop = time msg gets added to the network for easier calculations!
		message_queue_map[int(hour)].append(msg)
		total_messages2 += 1

	for current_day in list(range(start_day, end_day)):
		for current_hour in list(range(0,24)):
			network_state_new = defaultdict(set)
			current_data_file = DATA_FILE_PREFIX + str(city_number) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
			current_data_file_threshold = DATA_FILE_PREFIX + str(city_number) + "_" + str(threshold) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT

			if threshold != "0":
				current_data_file = current_data_file_threshold

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
					network_state_new[tower_id] = current_state
				"""
				previous_state = network_state[tower_id]
				transitions_added = new_state.difference(previous_state)
				transitions_removed = previous_state.difference(new_state)
				transitions_idle = new_state.intersection(previous_state)
				"""
				# print "Added: ", transitions_added
				# print "Removed: ", transitions_removed
			print("Users in all towers(double counted):", len(users_this_hour))
			message_hour = current_hour + (24 * (current_day - start_day))
			for msg in message_queue_map[message_hour]:

				if msg.src in message_queue:
					message_queue[msg.src][msg.id] = [msg.trust, msg]
				else:
					message_queue[msg.src] = {msg.id: [msg.trust, msg]}

				dirty_nodes.append(msg.src)
				total_messages1 += 1

			users_this_hour = set(users_this_hour)
			print("Users seen this hour: ", len(users_this_hour))
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
			print("Network changes added: ", len(changes_added), " removed: ", len(changes_removed))
			print("Total dirty nodes: ", len(dirty_nodes))
			first_state = False
			print("Simulating message exchange on all nodes that belong to a network.")
			queue_occupancy[str(current_day) + "," + str(current_hour)] = defaultdict()
			for tower in network_state_new.keys():
				users_in_tower = network_state_new[tower]
				perform_sybil_exchanges(sybil_number, tower, users_in_tower, current_day, current_hour)
				if queuesize == 0:
					if perform_message_exchanges(users_in_tower, current_day, current_hour):
						dirty_nodes += users_in_tower
					else:
						pass
				else:
					if perform_message_exchanges_with_queue(users_in_tower, queuesize, current_day, current_hour, trust_scores_file):
						dirty_nodes += users_in_tower
					else:
						pass

			#before: iterating through a dictionary
			#now: iterating through a dictionary
			for user in message_queue.keys():
				dellist = []
				#before: iterating through per user dictionary
				#after: iterating through the user queue

				for msgid, prio_tuple in message_queue[user].items():
					msg = prio_tuple[1]
					if msgid not in message_delivered[user]:
						if msg.dst == user and msgid:
							message_delivery_count += 1
							message_delivered[user].append(msgid)
							if msgid not in message_delays:
								hour_of_simulation = ((current_day - start_day)*24) + current_hour
								message_delays[msgid] = int(hour_of_simulation - int(msg.hop))
								print("Message delay: ", message_delays[msgid])
							msg.ttl = 60
						elif msg.ttl > 1:
							msg.ttl -= 1
						else:
							dellist.append(msgid)

				for id_ in dellist:
					del message_queue[user][id_]
				

			for key, value in network_state_new.items():
				network_state_old[key] = value
			dirty_nodes = []
			total_messages = total_messages1 if deliveryratiotype == 1 else total_messages2

			with open(result_file, "a+") as out_file:
				dlim = ','
				out_file.write(getline(current_day, current_hour, len(users_this_hour), len(dirty_nodes), message_delivery_count, total_messages))
				out_file.write("\n")
	with open(result_file_queue_occupancy, "w") as outfile:
		for day in list(range(start_day, end_day)):
			for hour in list(range(0,24)):
				key = str(day) + "," + str(hour)
				for user, queueocc in queue_occupancy[key].items():
					outfile.write(str(key) + "," + str(user) + "," + str(queueocc) + '\n')

	for user, msgids in message_delivered.items():
		for msgid in msgids:
			file_delay.write(str(msgid) + "," + str(message_delays[msgid]) + "\n")

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

def perform_sybil_exchanges(sybil_number, tower, users_in_tower, current_day, current_hour):
	for i in list(range(0, sybil_number)):
		id = str(tower) + "_" + str(current_day) + "_" + str(current_hour) + "_" + str(i)
		sybil_message = Message(id, 100, -1, -1, -1, 0)
		for u in users_in_tower:
			message_queue[u][sybil_message.id] = sybil_message

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


def perform_message_exchanges_with_queue(users, queuesize, current_day, current_hour, trust_scores_file):

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
			#######################################################

			#Exchanging all messages of u1 with u2
			#if u2 is present in trust_scores
			if trust_scores.get(u2) != None:				
				#set priority as 1 when copying the messages into the receiver u2
				if trust_scores[u2].get(u1) != None:
					#set priority as 1 for the incoming messages since they are from a trusted user
					#mq1_copy = dict(map(lambda x: (x[0], (1, x[1][1])),  mq1.items()))					
					#mq1_copy = {msgid: (1, prio_tuple[1]) for (msgid,prio_tuple) in mq1.items()}
					mq1_len = len(mq1)
					
					if len(mq2) < queuesize:
						mq2.update(mq1)
						for key in mq1.keys():
							mq2[key][0] = 1
					else:						
						mq2_sorted = sorted(mq2.items(), key=lambda x: x[1][0], reverse=True)[:-mq1_len or None]						
						#for counter in range(mq1_len):
						#	popped = mq2_sorted.pop()
							
						mq2 = dict(mq2_sorted)
						mq2.update(mq1)
						for key in mq1.keys():
							mq2[key][0] = 1	
						
				else:
					if len(mq2) < queuesize:
						#set priority as 0 for the incoming messages
						#mq1_copy = dict(map(lambda x: (x[0], (0, x[1][1])),  mq1.items()))
						#mq1_copy = {msg: (0, prio_tuple[1]) for (msg, prio_tuple) in mq1.items()}
						mq2.update(mq1)
						for key in mq1.keys():
							mq2[key][0] = 0

			else:
				if len(mq2) < queuesize:
					#mq1_copy = {msg: (0, prio_tuple[1]) for (msg, prio_tuple) in mq1.items()}
					#mq1_copy = dict(map(lambda x: (x[0], (0, x[1][1])),  mq1.items()))
					mq2.update(mq1)
					for key in mq1.keys():
						mq2[key][0] = 0


			#Exchanging all messages of u2 with u1

			#Repeat all of the above
			if trust_scores.get(u1) != None:
				if trust_scores[u1].get(u2) != None:
					#mq2_copy = {msg: (1, prio_tuple[1]) for (msg, prio_tuple) in mq2.items()}
					#mq2_copy = dict(map(lambda x: (x[0], (1, x[1][1])),  mq2.items()))
					mq2_len = len(mq2)
					if len(mq1) < queuesize:
						mq1.update(mq2)
						for key in mq2.keys():
							mq1[key][0] = 1
					else:
						mq1_sorted = sorted(mq1.items(), key=lambda x: x[1][0], reverse=True)[:-mq2_len or None]
						#for counter in range(mq2_len):
						#	popped = mq1_sorted.pop()
						mq1 = dict(mq1_sorted)
						mq1.update(mq2)
						for key in mq2.keys():
							mq1[key][0] = 1
						
				else:
					if len(mq1) < queuesize:
						 #mq2_copy = {msg: (0, prio_tuple[1]) for (msg, prio_tuple) in mq2.items()}
						 #mq2_copy = dict(map(lambda x: (x[0], (0, x[1][1])),  mq2.items()))
						 mq1.update(mq2)
						 for key in mq2.keys():
							 mq1[key][0] = 0

			else:
				if len(mq1) < queuesize:
					#mq2_copy = {msg: (0, prio_tuple[1]) for (msg, prio_tuple) in mq2.items()}
					#mq2_copy = dict(map(lambda x: (x[0], (0, x[1][1])),  mq2.items()))
					mq1.update(mq2)
					for key in mq2.keys():
						mq1[key][0] = 0

			#######################################################

			queue_occupancy[queue_key][u1] = len(mq1)
			queue_occupancy[queue_key][u2] = len(mq2)

	return len(dirty) > 0


if __name__ == "__main__":
	main()

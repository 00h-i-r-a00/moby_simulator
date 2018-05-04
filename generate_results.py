#!/usr/bin/env python
import sys
import matplotlib.pyplot as plt
import pdb
import json
import os
import csv
import pdb
import numpy as np

##Add two different list input parameters for queuesizes and queueoccupancy files

start_day = 20
end_day = 23

colors = ["#596ed8",
"#6ebe46",
"#9c54ca",
"#62a14e",
"#e555b3",
"#4cae87",
"#b0378b",
"#b8af46",
"#c983df",
"#d99234",
"#768dd1",
"#da5732",
"#45aecf",
"#d73e64",
"#69742e",
"#7c579c",
"#bd8953",
"#db84b4",
"#a14c2c",
"#9e4965",
"#df7d77",
"#698e98"]


print "Running"
#plt.subplot(211)
plt.xlabel('Hours')
plt.ylabel('Delivery Ratio')
dataset = []
configs = []
queue_occupancy_files = []
for f in sys.argv[1:]:
	print "Processing", f
	with open(f) as data:
		hour_list = []
		delivery_ratio = []
		hourctr = 0
		for entry in data:
			current_day, current_hour, number_of_users_this_hour, number_dirty_nodes_this_hour, message_delivery_count, total_messages\
					= entry.strip().split(",")
			hour_list.append(hourctr)
			hourctr += 1
			delivery_ratio.append(float(message_delivery_count)/int(1000))
	
	
	config_filename = os.getcwd() + '/ExperimentsData/data_all_thresholds_three_distributions/configs/' + f.split('/')[3].split('.')[0] + '.txt'
	
	queue_occupancy_files.append('ExperimentsData/data_all_thresholds_three_distributions/results/' + f.split('/')[3].split('.')[0] + '_queue_occupancy.csv')

	
	
	with open(config_filename, 'r') as f:
		configs.append(json.loads(f.readlines()[0]))
	
	dataset.append((hour_list, delivery_ratio))
	print "Filename %s" % (f)

	print "Maximum Del Ratio %f" %(max(delivery_ratio))
		
config_different_key_values = []
config_same_key_values = []

for key in configs[0].keys():
	x = []
	for config in configs:
		x.append(config[key])
	x = set(x)    
	if len(x) != 1:
		config_different_key_values.append(key)
		#~ if key != 'percentagehoursactive':
			#~ config_different_key_values.append(key)
	else:
		config_same_key_values.append(key)
		#~ if key != 'percentagehoursactive':
			#~ config_same_key_values.append(key)


i=0
for data in dataset:
	#for the corresponding config, get the values corresponding to the
	#keys that are different, and store it in legend
	legend = ''
	for key in config_different_key_values:
		legend += ' ' + key + ':' + str(configs[i][key])

	
	plt.plot(data[0], data[1], marker='o', label=legend, color=colors[i])
	plt.legend(fontsize=7, bbox_to_anchor=(1.1, 1.05))
	i+=1
title = ''
for key in config_same_key_values:
	title += key + ': ' + str(configs[0][key]) + '; '

title = 'Delivery Ratio Vs Hour for config: ' + title
plt.xticks(fontsize=7)
plt.yticks(fontsize=7)
plt.title(title, fontsize=7)
plt.show()


########Plotting Queue Occupancies and active users###############################

plt.subplot(211)

p=0
num_nan = []
for filename in queue_occupancy_files:
	queue_occupancy = {}
	##initialization
	for day in xrange(start_day,end_day):
		for hour in xrange(0, 24):
			key = str(day) + "," + str(hour)
			queue_occupancy[key] = []

	row_no=0
	
	with open(filename) as csvfile:
		datareader = csv.reader(csvfile, delimiter=',')
		try:
			for row in datareader:
				row_no += 1
				k = row[0] + "," + row[1]
				if row[3] != 'nan':
					queue_occupancy[k].append(int(row[3]))
					#if no user than row[3] == nan
				else:
					queue_occupancy[k].append(row[3])	
		except KeyError as exc:
			pdb.set_trace()					
	queue_occupancies = []      
	hours = [i for i in xrange(72)]
	max_queue_occs = []
	total = 0
	keys = []
	
	for key, value in queue_occupancy.iteritems(): 
		list_of_user_occupancies = queue_occupancy[key]
		isNan = [occ == 'nan' for occ in list_of_user_occupancies]
		if all(isNan):
			
			max_queue_occs.append(float('NaN'))
		else:
			try:
				if 'nan' in list_of_user_occupancies:
					list_of_user_occupancies = [value for value in list_of_user_occupancies if value != 'nan']	
					max_queue_occs.append(np.max(list_of_user_occupancies))
				else:
					max_queue_occs.append(np.max(list_of_user_occupancies))
					
			except TypeError as exc:
				print "Exception"
				
					
	
	legend = ''
	for key in config_different_key_values:
		legend += ' ' + key + ':' + str(configs[p][key])

	
	plt.xticks(fontsize=7)
	plt.yticks(fontsize=7)
	#if len(max_queue_occs) == 72:
	print "Filename %s" % (filename)
	print "Maximum Queue Occupancy %d" %(max(max_queue_occs))
	y = np.array(max_queue_occs)
	#~ y = []
	#~ for i in xrange(len(max_queue_occs)):
		#~ if i%10 == 0:
			#~ y.append(float('NaN'))
		#~ else:
			#~ y.append(max_queue_occs[i])
	
	mask = np.isfinite(np.array(y))
	
	num_nan.append(len([i for i in mask if i == False]))
	
	y_ = np.array(y)[mask]
	
	line, = plt.plot(np.array(hours)[mask], y_,label=legend, color=colors[p], linestyle='--', lw=0.5)
	plt.plot(np.array(hours), y,label=legend, color=line.get_color(), lw=1)

	plt.legend(fontsize=7,  bbox_to_anchor=(1.1, 1.05))
	p +=1 
	
title = ''
for key in config_same_key_values:
	title += key + ': ' + str(configs[0][key]) + '; '

plt.title(title, fontsize=7)
########plotting active users##########

#~ ######writing data into files
DATA_FILE_PREFIX = "/home/hira/simulator/moby_simulator/data/"
DATA_FILE_FORMAT = ".twr"


city_number = 0
h = 0
f = open('/home/hira/moby_simulator_new/moby_simulator/ExperimentsData/data_all_thresholds_three_distributions/active_users.txt', 'w')
l = open('/home/hira/moby_simulator_new/moby_simulator/ExperimentsData/data_all_thresholds_three_distributions/active_users_leaving.txt', 'w')
e = open('/home/hira/moby_simulator_new/moby_simulator/ExperimentsData/data_all_thresholds_three_distributions/active_users_entering.txt', 'w')
#active_users_entering_2.txt represents 0 to 200 queuesize with increments of 10, 1000 messages, 100 to 103 days
h = 0
users_previous = []
from collections import defaultdict
				
for current_day in xrange(start_day, end_day):
	for current_hour in xrange(0,24):
		print "Processing for hour %d " %(h)
		network_state_new = defaultdict(set)
		current_data_file = DATA_FILE_PREFIX + str(city_number) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
		users_this_hour = []
		with open(current_data_file) as data:
			for entry in data:
				hour, tower_id, user_ids = entry.split(",")
				user_ids = user_ids.strip()
				users_this_hour += user_ids.split("|")
		users_this_hour = set(users_this_hour)
		users_old = set(users_previous).intersection(set(users_this_hour))
		users_entering = [user for user in users_this_hour if user not in users_old]
		users_leaving = [user for user in users_previous if user not in users_this_hour]
		
		users_previous = users_this_hour
		 ## users that were there in the previous that are still there in the current hour
		#print "Users Entering hour %d: %d" %(h, len(users_entering))
		#print "Users Leaving hour %d: %d" %(h, len(users_leaving))
		#print "Users Active hour %d: %d" %(h, len(users_this_hour))
		if len(users_this_hour) != 0:
			x = 0   
			for user in users_this_hour:
				x+=1
				f.write(str(h) + ',' + str(user) + '\n' )
				#print "Active Users written %d times" %(x)
		else:
		
			f.write(str(h) + ',nouser' + '\n')
			
		if len(users_entering) != 0:
			x = 0   
			for user in users_entering:
				x+=1
				e.write(str(h) + ',' + str(user) + '\n')
				#print "Active Users written %d times" %(x)
		else:
			e.write(str(h) + ',nouser' + '\n')
			
		if len(users_leaving) != 0:
				
			for user in users_leaving:
				l.write(str(h) + ',' + str(user) + '\n')        
		else:
			l.write(str(h) + ',nouser' + '\n')
		
		h+=1                
			
e.close()   
l.close()
f.close()

def plot_users(figno, userfile, title):
		
	active_users = {}
	with open('/home/hira/moby_simulator_new/moby_simulator/' + userfile, 'r') as f:
		for line in f:
			line = line.split(',')
			
			if line[0] in active_users:
				active_users[line[0]].append(line[1])
			else:
				active_users[line[0]] = [line[1]]
	
	counts = []
	for i in xrange(72):
		if 'nouser' not in active_users[str(i)]:
			counts.append(len(active_users[str(i)])) 
		else:
			counts.append(0)
			
	
	hours = [i for i in xrange(72)]
	#plt.subplots_adjust(left=0.06, bottom=0.08, right=0.97, top=0.96, wspace=0.20, hspace=0.33)
	
	plt.title(title, fontsize=7)
	plt.xticks(fontsize=7)
	plt.yticks(fontsize=7)
	plt.xlabel('Hours', fontsize=7)
	plt.ylabel('Number of Active Users',fontsize=7) 

	plt.plot(hours, counts, label=title)
	
	plt.legend(fontsize=7)
	

##plotting
plt.subplot(212)

filenames = ['/ExperimentsData/data_all_thresholds_three_distributions/active_users.txt', 
'/ExperimentsData/data_all_thresholds_three_distributions/active_users_entering.txt',
 '/ExperimentsData/data_all_thresholds_three_distributions/active_users_leaving.txt']
titles = ['Active Users Per Hour', 'Active Users Entering Per Hour', 'Active Users Leaving Per Hour']
	
	#plt.subplot(212)
for k in xrange(len(filenames)):
	plot_users(k+2, filenames[k], titles[k])
plt.show()  


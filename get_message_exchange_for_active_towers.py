import pdb
import matplotlib.pyplot as plt
from collections import defaultdict
import sys

start_day = 21
end_day = 24

DATA_FILE_PREFIX = "data/"
DATA_FILE_FORMAT = ".twr"
city_number = 0	
def main():	
	log_filename = sys.argv[1]
	towers_no_message_exchange_each_hour = defaultdict(int)
	
	with open(log_filename, 'r') as lines:
		for line in lines:
			if 'Message Exchange Did Not Occur' in line:
		
				line = line.strip().split(' ')
				day = line[7].replace(',','')
				hour = line[9] 
				
				key = str(day) + ',' + str(hour)
				
				towers_no_message_exchange_each_hour[key] += 1
	
	active_towers = defaultdict(int)
	message_exchanging_towers = defaultdict(int)
	
	for current_day in xrange(start_day, end_day):
		for current_hour in xrange(0,24):
			key = str(current_day) + ',' + str	(current_hour)
			network_state_new = defaultdict(set)
			current_data_file = DATA_FILE_PREFIX + str(city_number) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
			users_this_hour = []
			print "Processing hour: ", current_hour, " File: ", current_data_file
			with open(current_data_file) as data:
				for entry in data:
					# Just calcuate this hours state, no modification to last hour.
					# All modifications and related logic at the end of the hour.
					hour, tower_id, user_ids = entry.split(",")
					user_ids = user_ids.strip()
					users_this_hour += user_ids.split("|")
					current_state = set(user_ids.split("|"))
					
					active_towers[key] += 1
			if key not in towers_no_message_exchange_each_hour:
				towers_no_message_exchange_each_hour[key] = 0
	
			message_exchanging_towers[key] = active_towers[key] - towers_no_message_exchange_each_hour[key]				


	hours = [i for i in xrange(72)]
	
	print len(active_towers.values())
	print len(message_exchanging_towers.values())
	print len(towers_no_message_exchange_each_hour.values())

	plt.plot(hours, active_towers.values(), label='Active Towers')
	plt.plot(hours, message_exchanging_towers.values(), label='Towers Exchanging Messages')
	plt.plot(hours, towers_no_message_exchange_each_hour.values(), label='Towers Not Exchanging Messages')
	plt.title('Activity of Towers', fontsize=10)
	plt.ylabel('Number of Towers', fontsize=7)
	plt.xlabel('Hours', fontsize=7)
	plt.legend(bbox_to_anchor=(1.1, 1.05), fontsize=7)
	plt.show()		
	"""
	
	"""

if __name__ == "__main__":
	main()

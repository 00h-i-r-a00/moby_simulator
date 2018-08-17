import os
from collections import defaultdict
import argparse
import pdb
import sys

DATA_FILE_PREFIX = 'data/'
DATA_FILE_FORMAT = '.twr'
city=0

def main():
	
	
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-t', '--thresholds', help='thresholds', type=int, nargs='+', default=0)
	parser.add_argument('-n', '--numdays', help='number of days', type=int, nargs='+', default=0)
	parser.add_argument('-d', '--dayrange', help='Total days in the year', type=int, nargs='?', default=0)

	args = parser.parse_args(sys.argv[1:])
	thresholds = args.thresholds
	numdays = args.numdays
	daysrange = args.dayrange

#create folders

	for threshold in thresholds:
		for day in xrange(daysrange + 1):
			for num_days in numdays:
				folder = os.getcwd() + '/' + DATA_FILE_PREFIX + str(city) + "_" + str(threshold) + "/" + str(day) + "/" + str(num_days)
				if not os.path.exists(folder):
					os.makedirs(folder)
				  		
	for threshold in thresholds:
		for num_days in numdays:
			for day in xrange(daysrange + 1):
				#get userpool for threshold, num_days and the particular starting day
				
				userpool = defaultdict(int)
				print "Processing for threshold %d day %d and num_days %d" %(threshold, day, num_days)					 
				########compute userpool over the the num_day period 
				
				for current_day in xrange(day, day + num_days):
					for current_hour in xrange(0,24):
						print "day: %d, hour: %d, threshold: %d, numday: %d" %(current_day, current_hour, threshold, num_days)
						current_data_file = os.getcwd() + '/' + DATA_FILE_PREFIX + str(city) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
						users_this_hour = []
						with open(current_data_file) as data:
							for entry in data:
								hour, tower_id, user_ids = entry.split(",")
								user_ids = user_ids.strip()
								users_this_hour += user_ids.split("|")
						
						users_this_hour = set(users_this_hour)
			
								
						for u in users_this_hour:
							userpool[u] += 1
				
				userpool = dict((k, v) for (k, v) in userpool.iteritems() if v >= threshold)
						
				for current_day in xrange(day, day + num_days):
					for current_hour in xrange(0,24):
						prefolder = os.getcwd() + "/" + DATA_FILE_PREFIX + str(city) + "_" + str(threshold) + "/" + str(day) + "/" + str(num_days)
						current_output_data_file = prefolder + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT                  
						thresh_out = open(current_output_data_file, 'w')
						current_data_file = DATA_FILE_PREFIX + str(city) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
						users_this_hour = []
						print "Filtering Users : day %d , hour %d num_days %d" %(current_day, current_hour, num_days)
						with open(current_data_file) as data:
							for entry in data:
								hour, tower_id, user_ids = entry.split(",")
								user_ids = user_ids.strip().split("|")
								threshold_users_per_tower = [user for user in user_ids if userpool.get(user) != None] 

								if len(threshold_users_per_tower) != 0:
									out_row = hour + "," + tower_id + "," + "|".join(threshold_users_per_tower)
									thresh_out.write(out_row + "\n")
						thresh_out.close()
		
if __name__ == "__main__":
	main()
		

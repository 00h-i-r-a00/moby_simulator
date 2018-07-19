from __future__ import division
import pdb
import argparse
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
import os
import csv
import numpy as np
from argparse import RawTextHelpFormatter
import functools
import pdb

mpl.rcParams['lines.linewidth'] = 2
mpl.rcParams['figure.titlesize'] = 'large'
mpl.rcParams['figure.titleweight'] = 'normal'
mpl.rcParams['figure.figsize'] = '19, 12'
mpl.rcParams['figure.dpi'] = '100'
mpl.rcParams['figure.facecolor'] = 'white'
mpl.rcParams['figure.edgecolor'] = 'white'
mpl.rcParams['figure.subplot.left']  = '0.125'  # the left side of the subplots of the figure
mpl.rcParams['figure.subplot.right']   = '0.65'    # the right side of the subplots of the figure
mpl.rcParams['figure.subplot.bottom']  = '0.11'    # the bottom of the subplots of the figure
mpl.rcParams['figure.subplot.top'] = '0.88'    # the top of the subplots of the figure
mpl.rcParams['figure.subplot.wspace']  = '0.2'    # the amount of width reserved for blank space between subplots,
								 # expressed as a fraction of the average axis width

#running string
#python generate_results_aggregate.py --ttls 12 24 --start-days 53 --numdays 3 4 5 --city-numbers 0 --number 30000 --thresholds 0 2 4 6 8 10 12 --cooldowns 24 --seeds 244896923 --queuesizes 0 --percentagehoursactive 50 --messagegenerationtype 1 --deliveryratiotype 1 --distributiontype region_sms_based --sybil-number 0 --single --foldername ExperimentsData/data_42_simulations_38_succeeded --plottypes 1 2 3 4 5 6

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

"""
1. plot delivery ratio
2. plot queue occupancy
3. get maximum delivery ratios for all configurations
4. get maximum queue occupancies

"""
#TODO
def get_config_similarity(configs):

	"""
	gets the keys that have the same/different values

	"""
	pass

def get_delivery_ratios(plot_number, configs, args, type_):
	##configs conts filepaths to configs

	configs_content = []
	dataset = []
	#if single

	for f in configs:

		#assumes the format that configs is in the same folder as the results (i.e the folder with the results referred to by args.foldername)

		f_ = f.replace('configs', 'results')
		f_ = f_.replace('.txt', '.csv')

		with open(f_) as data:
			hour_list = []
			delivery_ratio = []
			hourctr = 0
			for entry in data:
				current_day, current_hour, number_of_users_this_hour, number_dirty_nodes_this_hour, message_delivery_count, total_messages\
				= entry.strip().split(",")
				hour_list.append(hourctr)
				hourctr += 1
				delivery_ratio.append(float(message_delivery_count)/int(args.number[0]))

		with open(f, 'r') as fi:
			configs_content.append(json.loads(fi.readlines()[0]))

		dataset.append((hour_list, delivery_ratio))

	config_different_key_values = []
	config_same_key_values = []

	#TODO: more efficient way to do this
	#keys = [set(configs_content[i].keys()) for i in xrange(len(configs_content))]
	#use functools and the reduce function

	for key in configs_content[0].keys():
		x = []
		for config in configs_content:
			x.append(config[key])
		x = set(x)
		if len(x) != 1:
			config_different_key_values.append(key)
		else:
			config_same_key_values.append(key)

	title = ''

	#title ~ attributes that are common to all the simulations

	for key in config_same_key_values:
		title += key + ': ' + str(configs_content[0][key]) + '; '

	if type_ == 'plot':
		fig = plt.figure()
		title = "Configuration Parameters in Common: " + title
		fig.text(.5, .05, title, ha='center')
		#if single
		if plot_number[0]:
			i=0
			for data in dataset:
			#for the corresponding config, get the values corresponding to the
			#keys that are different, and store it in legend
				legend = ''
				for key in config_different_key_values:
					legend += ' ' + key + ':' + str(configs_content[i][key])



				plt.plot(data[0], data[1], marker='o', label=legend, color=colors[i])
				plt.legend(fontsize=10, bbox_to_anchor=(1.1, 0.75), loc='upper left')
				i+=1

			title = 'Delivery Ratio Vs Hour \n Configuration: ' + title
			plt.xticks(fontsize=8)
			plt.yticks(fontsize=8)
			#plt.title(title, fontsize=9)
			plt.xlabel('Hours', fontsize=9)
			plt.ylabel('Delivery Ratio', fontsize=9)
			figname = 'plot_'
			figname = figname + '_deliveryratio.png'
			plt.savefig(os.getcwd() + '/' + args.outputfoldername + '/' + figname)

	if type_ == 'maximumandfinal':

		outf = open(os.getcwd() + '/' + args.outputfoldername + '/' + 'maxandmin_del_ratios.csv', 'w')
		colnames = 'Configuration Type ,Maximum Delivery Ratio Hour,Maximum Delivery Ratio,Minimum Delivery Ratio Hour,Minimum Delivery Ratio'
		outf.write('Configuration Parameters in Common: ' + title + ',,,,\n')
		outf.write(colnames + '\n')

		for index, config in enumerate(configs):
			current_del_ratios = dataset[index][1]
			maximum_del_ratio = max(current_del_ratios)
			maximum_del_ratio_ind = current_del_ratios.index(maximum_del_ratio)
			max_hour = dataset[index][0][maximum_del_ratio_ind]

			minimum_del_ratio = min(current_del_ratios)
			minimum_del_ratio_ind = current_del_ratios.index(minimum_del_ratio)
			min_hour = dataset[index][0][minimum_del_ratio_ind]

			#config = config.replace(os.getcwd() + '/' +  args.foldername + '/configs/', '')
			config_string = '::'.join([str(key) + ':' + str(value) for key, value in configs_content[index].iteritems()])
			outf.write(config_string + ',' + str(max_hour) + ',' + str(maximum_del_ratio) + ',' + str(min_hour) + ', ' + str(minimum_del_ratio) + '\n')

		outf.close()


def get_attribute_value_of_config(config_file_path, attribute):

	with open(config_file_path, 'r') as f:
		config_dict = json.loads(f.readlines()[0])

	return config_dict[attribute]

def get_queue_occupancy(plot_number, configs, args, type_):

	p=0
	num_nan = []
	##get config contents
	##get start day and end day from there
	queue_occupancy_files = [fi.replace('configs', 'results').replace('.txt', '_queue_occupancy.csv') for fi in configs]

	configs_content = []

	for f in configs:
		with open(f, 'r') as fi:
			configs_content.append(json.loads(fi.readlines()[0]))

	config_different_key_values = []
	config_same_key_values = []

	for key in configs_content[0].keys():
		x = []
		for config in configs_content:
			x.append(config[key])
		x = set(x)
		if len(x) != 1:
			config_different_key_values.append(key)
		else:
			config_same_key_values.append(key)


	
	max_queue_occs_per_configuration = []
	hours_per_configuration = []
	
	for filename in queue_occupancy_files:
		queue_occupancy = {}
		##initialization
		config_file = filename.replace('results', 'configs').replace('_queue_occupancy.csv', '.txt')
		endday = get_attribute_value_of_config(config_file, 'end-day')

		max_hours = 0
		
		#initialize a dictionary for each file
		#containing key as day and hour
		#value as a list which is to contain all the queue occupancies noted for that day and hour by all usrs
		for day in xrange(args.start_days[0], int(endday)):
			for hour in xrange(0, 24):
				key = str(day) + "," + str(hour)
				queue_occupancy[key] = []
				max_hours += 1

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
				print exc
		queue_occupancies = []

		hours = [i for i in xrange(max_hours)]
		max_queue_occs = [] #maximum queue occupancy at that hour for a single configuration
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
					print exc
					
		max_queue_occs_per_configuration.append(max_queue_occs)
		hours_per_configuration.append(hours)
		title = ''
		
		for key in config_same_key_values:
			 title += key + ': ' + str(configs_content[0][key]) + '; '

		if type_ == 'plot':
			
			fig = plt.figure()
			title = "Configuration Parameters in Common: " + title
			fig.text(.5, .05, title, ha='center')
			
			
			for index, queue_occupancies in enumerate(max_queue_occs_per_configuration):
				hours = hours_per_configuration[index]
				legend = ''
	
				for key in config_different_key_values:
					legend += ' ' + key + ':' + str(configs_content[index][key])
	
	
				plt.xticks(fontsize=7)
				plt.yticks(fontsize=7)
				y = np.array(queue_occupancies)
				mask = np.isfinite(np.array(y))
	
				num_nan.append(len([i for i in mask if i == False]))
	
				y_ = np.array(y)[mask]
	
				line, = plt.plot(np.array(hours)[mask], y_,label=legend, color=colors[index], linestyle='--', lw=0.5)
				plt.plot(np.array(hours), y,label=legend, color=line.get_color(), lw=1)
	
				plt.legend(fontsize=7,  bbox_to_anchor=(1.1, 1.05), loc='upper left')
				#p +=1	
				#plt.title(title, fontsize=7)
				
			figname = 'plot_'
			figname = os.getcwd() + '/' + args.outputfoldername + '/' + figname + '_queuecoccupancy.png'
			plt.savefig(figname)

		elif type_ == 'maximum':
			
			outf = open(os.getcwd() + '/' + args.outputfoldername + '/' + '_maximum_queue_occupancy.csv', 'w')
			outf.write('Configuration Parameters in Common: ' + title + ',\n')
			outf.write('Configuration Name,Maximum Queue Occupancy' + '\n')
			for index, queue_occupancies in enumerate(max_queue_occs_per_configuration):
				max_queue = max(queue_occupancies)
				config_string = '::'.join([str(key) + ':' + str(value) for key, value in configs_content[index].iteritems()])
				outf.write(config_string + ',' + str(max_queue) + '\n')

def plot_active_users(start_day, end_day):
	pass

def get_delays(plot_number, configs, args, type_):

	configs_content = []

	for f in configs:
		with open(f, 'r') as fi:
			configs_content.append(json.loads(fi.readlines()[0]))

	config_different_key_values = []
	config_same_key_values = []

	for key in configs_content[0].keys():

		x = []
		for config in configs_content:
			x.append(config[key])
		x = set(x)
		if len(x) != 1:
			config_different_key_values.append(key)
		else:
			config_same_key_values.append(key)

	average_delays = []
	cellText = []

	for fi in configs:

		delays = []
		fi_ = fi.replace('configs', 'results').replace('.txt', '_message_delays.csv')
		with open(fi_) as csvfile:
			datareader = csv.reader(csvfile, delimiter=',')
			for row in datareader:
				delays.append(int(row[1]))

			average_delay = sum(delays)/len(delays)
			celltext = ''
			with open(fi, 'r') as f:
				config_content = json.loads(f.readlines()[0])
			for key in config_different_key_values:
				celltext += str(key) + ": " + str(config_content[key]) + "; "

			cellText.append([celltext, average_delay])


	cellText.sort(key = lambda x: x[1])


	if type_ == 'averagedelaystable':

		tabledata = ''
		for row in cellText:

			tabledata += str(row[0]) + ',' + str(row[1]) + '\n'

		colLabels = 'Configuration Name,Average Delay'


		title = ''
		for key in config_same_key_values:
			title += str(key) + ': ' + str(configs_content[0][key]) + "; "


		tabledata = colLabels + '\n' + tabledata


		outf = os.getcwd() + '/' + args.outputfoldername + '/' + 'table_messagedeliverytimes.csv'
		
		with open(outf, 'w') as f:
			f.write('Configuration Parameters in common :' + title + ',\n')
			f.write(tabledata)

		print "Message Delivery Times/Delays written in the table: " + outf


	elif type_ == 'maxandmin':

		ind = 1
		for row in cellText:
			if ind == 1:
				minimum_value = row[1]
				minimum_config = row[0]

			elif ind == len(cellText):

				maximum_value = row[1]
				maximum_config = row[0]

			ind += 1

		colLabels = 'Configuration Name,Average Delay'

		title = ''
		for key in config_same_key_values:
			title += str(key) + ': ' + str(configs_content[0][key]) + "; "


		outf2 = os.getcwd() + '/' + args.outputfoldername + '/' + 'minmax_messagedeliverytimes.csv'

		with open(outf2, 'w') as f:
			f.write(title + '\n')
			#f.write(colLabels + '\n')
			f.write('Minimum Message Delivery Time: ' + str(minimum_value) + ' at config: ' + str(minimum_config) + '\n')
			f.write('Maximum Message Delivery Time: ' + str(maximum_value) + ' at config: ' + str(maximum_config) + '\n')

		print "Minimum and Maximum Message Delivery Times/Delays in the file: " + outf2


def get_configs(args):

	number_of_messages = args.number
	start_days = args.start_days
	#this is different than how its encoded in the simulator; numdays are more useful in the enumeration of configs;
	#having only end days doesn't tell us anything about the start-day/end-day combination
	number_of_days = args.numdays

	cities = args.city_numbers
	cooldowns =  args.cooldowns
	thresholds = args.thresholds
	ttls = args.ttls
	seeds = args.seeds
	queuesizes = args.queuesizes
	percentagehoursactive = args.percentagehoursactive
	messagegenerationtype = args.messagegenerationtype
	deliveryratiotype = args.deliveryratiotype
	distributiontype = args.distributiontype
	sybils = args.sybil_number

	configs_to_plot = []
	configs_ = 0
	for val_ttl in ttls:
		for val_start in start_days:
			for val_nod in number_of_days:
				for val_city in cities:
					for val_cd in cooldowns:
						for val_nm in number_of_messages:
							for val_queue in queuesizes:
								for val_seed in seeds:
									for val_msgtype in messagegenerationtype:
										for val_active in percentagehoursactive:
											for val_delratio in deliveryratiotype:
												for val_disttype in distributiontype:
													for val_threshold in thresholds:
														for val_sybils in sybils:
															config = {}
															config["ttl"] = val_ttl
															config["start-day"] = val_start
															config["end-day"] = val_start+val_nod
															config["city-number"] = val_city
															config["cooldown"] = val_cd
															config["number"] = val_nm
															config["queuesize"] = val_queue
															config["seed"] = val_seed
															config["messagegenerationtype"] = val_msgtype
															config["percentagehoursactive"] = val_active
															config["deliveryratiotype"] = val_delratio
															config["distributiontype"] = val_disttype
															config["threshold"] = val_threshold
															config["sybil-number"] = val_sybils
															configs_to_plot.append(config)
															configs_ += 1


	foldername = os.getcwd() + '/' + args.foldername + '/configs/'
	files = os.listdir(foldername)
	file_paths = [foldername + f for f in files]

	configs_total = []
	for fi in file_paths:
		with open(fi) as in_:
			config = json.load(in_)
			configs_total.append(config)

	config_files_to_plot = []
	for index, config1 in enumerate(configs_total):
		for config2 in configs_to_plot:
			z = config1.pop('configuration', None)

			if config1 == config2:

				config_files_to_plot.append(file_paths[index])
				break

	return config_files_to_plot



def main():

	parser = argparse.ArgumentParser(description='Moby message generation script script.', formatter_class=RawTextHelpFormatter )
	parser.add_argument('--number', help='Number of messages to generate', type=int, nargs='+')
	parser.add_argument('--start-days', help='start day of the year', type=int, nargs='+')
	parser.add_argument('--numdays', help='number of days that the simulation needs to run', type=int, nargs='+')
	parser.add_argument('--configurations', help='Configuration and message file id', type=str, nargs='+')
	parser.add_argument('--city-numbers', help='City to generate messages for', type=int, nargs='+')
	parser.add_argument('--thresholds', help='Minimum occourances to be considered a legit user', type=int, nargs='+')
	parser.add_argument('--cooldowns', help='Cooldown hours, messages distributed over total hours - cooldown hours.', type=int, nargs='+')
	parser.add_argument('--ttls', help='The time to live to be used for the messages', type=int, nargs='+')
	parser.add_argument('--seeds', help='Number to use for random seeding', type=int, nargs='+')
	parser.add_argument('--queuesizes', help='0 if no queuesize else a specific number with the queuesize value', type=int, nargs='+')
	parser.add_argument('--percentagehoursactive', help='Percentage of hours the destinations stay active', type=int, nargs='+')
	parser.add_argument('--deliveryratiotype', help='1 if total_messages == upto that hour; 2 if total_messages == total number of messages in all hours', type=int, nargs='+')
	parser.add_argument('--messagegenerationtype', help='Original Criteria or Selectively changing sources and destinations', type=int, nargs='+')
	parser.add_argument('--distributiontype', help='2 types -> "uniform" or "user-activity-based" ; used in conjunction with messagegenerationtype', type=str, nargs='+')
	parser.add_argument('--sybil-number', help='number of sybils', type=int, nargs='+')
	parser.add_argument('--single', help='Use this flag to plot everything on a single plot', action='store_true')
	parser.add_argument('--multiple', help='Use this flag to plot everything on multiple plots', action='store_true')
	parser.add_argument('--useconfigs', help='Use this flag to specify specific configurations to plot', action='store_true')
	parser.add_argument('--foldername', help='Name of the folder with all the results', nargs='?', type=str)
	parser.add_argument('--plottypes', help='Specify plot types. \n 1. get delivery ratio plots' +
																 '\n 2. get queue occupancy plots '
																 '\n 3. get maximum and final delivery ratios' +
																 '\n 4. get maximum queue occupancies' +
																 '\n 5. get average delays in a table' +
																 '\n 6. get minimum and maximum delays'
																 , nargs='+', type=int)
	parser.add_argument('--outputfoldername', type=str, nargs='?')

	args = parser.parse_args(sys.argv[1:])
	print args

	#create the output folder
	if not os.path.exists(os.getcwd() + '/' + args.outputfoldername):
		os.makedirs(os.getcwd() + '/' + args.outputfoldername)

	useconfigs = args.useconfigs
	plottypes = args.plottypes

	if useconfigs:
		#contains the paths of all the configs to plot
		configs = [os.getcwd() + '/' + args.foldername + '/configs/' + f for f in args.configurations]

	else:
		#contains the paths of all the configs to plot
		configs = get_configs(args)

#    for i in xrange(1, 6):

	num_of_plots = (args.single, args.multiple)

	for plot in plottypes:

		if plot == 1:
			get_delivery_ratios(num_of_plots, configs, args, 'plot')

		elif plot == 2:
			get_queue_occupancy(num_of_plots, configs, args, 'plot')

		elif plot == 3:
			get_delivery_ratios(num_of_plots, configs, args, 'maximumandfinal')

		elif plot == 4:
			get_queue_occupancy(num_of_plots, configs, args, 'maximum')

		elif plot == 5:
			get_delays(num_of_plots, configs, args, 'averagedelaystable')

		elif plot == 6:
			get_delays(num_of_plots, configs, args, 'maxandmin')


if __name__ == "__main__":
	main()

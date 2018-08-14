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
import seaborn as sns
import pandas as pd
from math import isnan
<<<<<<< HEAD
from collections import defaultdict
=======
>>>>>>> aa8721ca9cec59a980ff7130096e8e59e1fc85a3

mpl.rcParams['lines.linewidth'] = 2
mpl.rcParams['figure.titlesize'] = 'large'
mpl.rcParams['figure.titleweight'] = 'normal'
mpl.rcParams['figure.figsize'] = '19, 12'
mpl.rcParams['figure.dpi'] = '100'
mpl.rcParams['figure.facecolor'] = 'white'
mpl.rcParams['figure.edgecolor'] = 'white'
mpl.rcParams['figure.subplot.left']  = '0.125'  # the left side of the subplots of the figure
mpl.rcParams['figure.subplot.right']   = '0.9'    # the right side of the subplots of the figure
mpl.rcParams['figure.subplot.bottom']  = '0.11'    # the bottom of the subplots of the figure
mpl.rcParams['figure.subplot.top'] = '0.88'    # the top of the subplots of the figure
mpl.rcParams['figure.subplot.wspace']  = '0.2'    # the amount of width reserved for blank space between subplots,
mpl.rcParams['figure.subplot.hspace']  = '0.53'
								 # expressed as a fraction of the average axis width



#running string
#python generate_results_aggregate.py --ttls 12 24 --start-days 53 --numdays 3 4 5 --city-numbers 0 --number 30000 --thresholds 0 2 4 6 8 10 12 --cooldowns 24 --seeds 244896923 --queuesizes 0 --percentagehoursactive 50 --messagegenerationtype 1 --deliveryratiotype 1 --distributiontype region_sms_based --dos-number 0 --single --foldername ExperimentsData/data_42_simulations_38_succeeded --plottypes 1 2 3 4 5 6

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
"#698e98"

]

"""
1. plot delivery ratio
2. plot queue occupancy
3. get maximum delivery ratios for all configurations
4. get maximum queue occupancies

"""
#TODO
def get_config_similarity(configs_content):

	"""
	gets the keys that have the same/different values

	"""
	same = []
	different = []
<<<<<<< HEAD

=======

>>>>>>> aa8721ca9cec59a980ff7130096e8e59e1fc85a3
	for key in configs_content[0].keys():

		x = []
		for config in configs_content:
			x.append(config[key])
		x = set(x)
		if len(x) != 1:
			different.append(key)
		else:
			same.append(key)

	return different, same

def get_delivery_ratios(plot_number, configs, args, type_):
	##configs conts filepaths to configs
	configs_content = []
	dataset = []

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

	config_different_key_values, config_same_key_values = get_config_similarity(configs_content)

	title = ''

	#title ~ attributes that are common to all the simulations

	for key in config_same_key_values:
		title += key + ': ' + str(configs_content[0][key]) + '; '

	if type_ == 'pdrvalues':
		return dataset

	if type_ == 'plot':
		fig = plt.figure()
		title = "Configuration Parameters in Common: " + title
		fig.text(.5, .05, title, ha='center')
		#if single
		if plot_number[0]:
			i=0
			for data in dataset:
				try:
			#for the corresponding config, get the values corresponding to the
			#keys that are different, and store it in legend
					legend = ''
					for key in config_different_key_values:
						legend += ' ' + key + ':' + str(configs_content[i][key])


					plt.plot(data[0], data[1], marker='o', label=legend, color=colors[i])
					plt.legend(fontsize=10, bbox_to_anchor=(1.1, 0.75), loc='upper left')
					i+=1
				except Exception as exc:
					pass
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

		tuples_to_plot = []
		for index, config in enumerate(configs):
			current_del_ratios = dataset[index][1]
			maximum_del_ratio = max(current_del_ratios)
			maximum_del_ratio_ind = current_del_ratios.index(maximum_del_ratio)
			max_hour = dataset[index][0][maximum_del_ratio_ind]

			minimum_del_ratio = min(current_del_ratios)
			minimum_del_ratio_ind = current_del_ratios.index(minimum_del_ratio)
			min_hour = dataset[index][0][minimum_del_ratio_ind]

			#config = config.replace(os.getcwd() + '/' +  args.foldername + '/configs/', '')
			config_string = '::'.join([str(key) + ':' + str(value) for key, value in configs_content[index].iteritems() if key in config_different_key_values])
			tuples_to_plot.append((config_string, max_hour, maximum_del_ratio, min_hour, minimum_del_ratio))
			#outf.write(config_string + ',' + str(max_hour) + ',' + str(maximum_del_ratio) + ',' + str(min_hour) + ', ' + str(minimum_del_ratio) + '\n')

		tuples_to_plot.sort(lambda z,y: cmp(z[2], y[2]))
		##writing down in a file

		outf = open(os.getcwd() + '/' + args.outputfoldername + '/' + 'maxandmin_del_ratios.csv', 'w')
		colnames = 'Configuration Type,Maximum Delivery Ratio Hour,Maximum Delivery Ratio,Minimum Delivery Ratio Hour,Minimum Delivery Ratio'
		outf.write('Configuration Parameters in Common: ' + title + ',,,,\n')
		outf.write(colnames + '\n')

		for item in tuples_to_plot:
			string = ','.join([str(i) for i in item])
			outf.write(string + '\n')

		outf.close()

	if type_ == 'heatmap':
		if len(dataset) == 1:
			current_del_ratios = dataset[0][1]
			maximum_del_ratio = max(current_del_ratios)
			return maximum_del_ratio


def get_attribute_value_of_config(config_file_path, attribute):

	with open(config_file_path, 'r') as f:
		config_dict = json.loads(f.readlines()[0])

	return config_dict[attribute]

def get_queue_occupancy(plot_number, configs, args, type_):

	p=0
	num_nan = []
	queue_occupancy_files = [fi.replace('configs', 'results').replace('.txt', '_queue_occupancy.csv') for fi in configs]
	configs_content = []

	for f in configs:
		with open(f, 'r') as fi:
			configs_content.append(json.loads(fi.readlines()[0]))

	config_different_key_values, config_same_key_values  = get_config_similarity(configs_content)

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

		###processing all the queue_occupancy to get the maximum queue occupancies
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

	if type_ == 'values':
		return hours_per_configuration, max_queue_occs_per_configuration

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
			config_string = '::'.join([str(key) + ':' + str(value) for key, value in configs_content[index].iteritems() if key in config_different_key_values])
			outf.write(config_string + ',' + str(max_queue) + '\n')

	elif type_ == 'heatmap':
		#assume just one value

		for index, queue_occupancies in enumerate(max_queue_occs_per_configuration):
			max_queue = max(queue_occupancies)

		return max_queue

def plot_active_users(start_day, end_day):
	pass

def get_delays(plot_number, configs, args, type_):

	configs_content = []

	for f in configs:
		with open(f, 'r') as fi:
			configs_content.append(json.loads(fi.readlines()[0]))

	config_different_key_values, config_same_key_values = get_config_similarity(configs_content)

	average_delays = []
	cellText = []
	delay_values = []
	delays_per_message = []

	for fi in configs:

		delays = []
		fi_ = fi.replace('configs', 'results').replace('.txt', '_message_delays.csv')

		with open(fi_) as csvfile:
			hours = []
			delays_per_hour = []

			datareader = csv.reader(csvfile, delimiter=',')
			for row in datareader:
				delays.append(int(row[1]))
				delays_per_message.append(int(row[1]))
				delays_per_hour.append(int(row[1]))

			average_delay = sum(delays)/len(delays)
			celltext = ''
			with open(fi, 'r') as f:
				config_content = json.loads(f.readlines()[0])
								#initialize; use later
			for key in config_different_key_values:
				celltext += str(key) + ": " + str(config_content[key]) + ":::"

			cellText.append([celltext, average_delay])
			delay_values.append(average_delay)

	cellText.sort(key = lambda x: x[1])

	if type_ == 'averagedelaystable':
				#table containing the average delays for all configurations
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
				#maximum and final values of the average delays
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

	elif type_ == 'heatmap':
		return delay_values

	elif type_ == 'delay_values':
		return delays_per_message

def get_configs(args):

	number_of_messages = args.number
	start_days = args.start_days
	#this is different than how its encoded in the simulator; numdays are more useful in the enumeration of configs;
	#having only end days doesn't tell us anything about the start-day/end-day combination
	number_of_days = args.numdays

	cities = args.city_numbers
	cooldowns =  args.cooldowns
	thresholds = args.thresholds
	#ttls = args.ttls
	seeds = args.seeds
	queuesizes = args.queuesizes
	percentagehoursactive = args.percentagehoursactive
	messagegenerationtype = args.messagegenerationtype
	deliveryratiotype = args.deliveryratiotype
	distributiontype = args.distributiontype
	doss = args.dos_number

	configs_to_plot = []
	configs_ = 0

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
													for val_doss in doss:
														config = {}
														config["ttl"] = val_nod * 24
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
														config["dos-number"] = val_doss
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
<<<<<<< HEAD

def extract_configs(configs, params_to_extract):
	"""
	params_to_extract = dictionary containing param: values pairs whose corresponding configs need to be extractedf

	"""
	new_configs = []

	num_params = len(params_to_extract.keys())


	for conf in configs:
		num_keys_present = 0
		with open(conf, 'r') as f:
			config_content = json.loads(f.readlines()[0])

		for key, value in params_to_extract.items():
			if config_content[key] == value:
				num_keys_present += 1


		if num_keys_present == num_params:
			new_configs.append(conf)
			num_keys_present = 0

	return new_configs

def plot_heatmap(dict_to_heatmap, configs, args, title):

	#dict_to_heatmap contains keys as start days and values as their corresponding metric values to plot
	# ~ columns_headings = []
	# ~ values = []

	#one conf should correspond with one start-day
	#this function is meant to plot a heatmap of 1 week only
	#dict_to_heatmap contains start_day --> average delay mappings
	# ~ for cons in configs:
		# ~ with open(cons, 'r') as f:
			# ~ conf = json.loads(f.readlines()[0])

		# ~ start_day = conf['start-day']
		# ~ columns_headings.append(start_day)
		# ~ values.append(dict_to_heatmap[start_day])

	# ~ columns_headings = [str(i) for i in columns_headings]
	# ~ #pdb.set_trace()
	# ~ df = pd.DataFrame(values, columns = [title])

	# ~ corr_matrix = df.corr()

	# ~ sns.heatmap(corr_matrix, cmap='PRGn')


	###create a matrix#####3
	pdb.set_trace()
	df = pd.DataFrame(dict_to_heatmap, index=args.start_days)
	fig = plt.figure(figsize=(12,12))
	r = sns.heatmap(df, cmap='BuPu')
	r.set_title("Heatmap for " + title)
	r.set_ylabel('First Day of the Week')
	r.set_xlabel('Number of Days for which Simulation was run')
	plt.show()


def get_heatmap(configs, args):

	start_days = args.start_days
	avg_delay_dict = defaultdict(list)
	max_pdr_dict = defaultdict(list)
	max_queue_occupancy = defaultdict(list)

	for num_day in [3, 4, 5]:
		for start_day in start_days:
			params_to_extract = {"start-day": start_day, "end-day": int(start_day) + num_day}
			configs_new = extract_configs(configs, params_to_extract)
			avg_delay_dict[str(num_day)].append(get_delays('single', configs_new, args, 'heatmap')[0])
			max_pdr_dict[str(num_day)].append(get_delivery_ratios('single', configs_new, args, 'heatmap'))
			max_queue_occupancy[str(num_day)].append(get_queue_occupancy('single', configs_new, args, 'heatmap'))

	plot_heatmap(avg_delay_dict, configs, args, 'Average Delay')
	plot_heatmap(max_pdr_dict, configs, args, 'Packet Delivery Ratio')
	#plot_heatmap(max_queue_occupancy, configs, args, 'Queue Occupancy')
=======
def extract_configs(configs, params_to_extract):
	"""
	params_to_extract = dictionary containing param: values pairs whose corresponding configs need to be extractedf

	"""
	new_configs = []

	for conf in configs:
		with open(conf, 'r') as f:
			config_content = json.loads(f.readlines()[0])

		for key, value in params_to_extract.items():
			if config_content[key] == value:
				new_configs.append(conf)

	return new_configs

def plot_heatmap(dict_to_heatmap, configs, title):

	#dict_to_heatmap contains keys as start days and values as their corresponding metric values to plot
	columns_headings = []
	values = []

	#one conf should correspond with one start-day
	#this function is meant to plot a heatmap of 1 week only
	#dict_to_heatmap contains start_day --> average delay mappings
	for cons in configs:
		with open(cons, 'r') as f:
			conf = json.loads(f.readlines()[0])

		start_day = conf['start-day']
		columns_headings.append(start_day)
		values.append(dict_to_heatmap[start_day])

	columns_headings = [str(i) for i in columns_headings]
	#pdb.set_trace()
	df = pd.DataFrame(values, columns = [title])

	corr_matrix = df.corr()

	sns.heatmap(corr_matrix, cmap='PRGn')



def get_heatmap(configs, args):

	start_days = args.start_days
	avg_delay_dict = {}
	max_pdr_dict = {}
	max_queue_occupancy = {}

	for start_day in start_days:
		params_to_extract = {"start-day": start_day}
		configs_new = extract_configs(configs, params_to_extract)
		#TODO: see how this is returned; need to change if there is an error
		avg_delay_dict[start_day] = get_delays('single', configs_new, args, 'heatmap')[0]
		max_pdr_dict[start_day] =  get_delivery_ratios('single', configs_new, args, 'heatmap')
		max_queue_occupancy[start_day] = get_queue_occupancy('single', configs_new, args, 'heatmap')

	plot_heatmap(avg_delay_dict, configs, 'Average Delay')
	plot_heatmap(max_pdr_dict, configs, 'Packet Delivery Ratio')
	plot_heatmap(max_queue_occupancy, configs, 'Queue Occupancy')


def get_embedded_graphs(configs, args):
	overall_best_pdr = []
	overall_max_queue = []

	start_days = args.start_days
	delays = []
	pdrs = []
	queue_occs = []
	maxPDR= 0
	maxQueue=0
	maxDelay = 0

	#to be used for subplots
	fig, axs = plt.subplots(len(start_days), 4)
	i=0

	pdr_xlim_min = []
	pdr_xlim_max = []
	pdr_ylim_max = []
	pdr_ylim_min = []

	qu_ylim_max = []
	qu_ylim_min = []

	for start_day in start_days:

		params_to_extract = {"start-day": start_day}
		configs_new = extract_configs(configs, params_to_extract)

		dataset = get_delivery_ratios('single', configs_new, args, 'pdrvalues')

		axs[i, 0].plot(dataset[0][0], dataset[0][1])
		pdr_xlim_min.append(min(dataset[0][0]))
		pdr_xlim_max.append(max(dataset[0][0]))
		pdr_ylim_min.append(min(dataset[0][1]))
		pdr_ylim_max.append(max(dataset[0][1]))

		maxPDR = max(dataset[0][1])
		hours_per_configuration, max_queue_occs_per_configuration = get_queue_occupancy('single', configs_new, args, 'values')
		overall_best_pdr.append(maxPDR)
		########################process queue occupancies########################################


		endday = get_attribute_value_of_config(configs_new[0], 'end-day')
		overall_max_queue.append(maxQueue)
		for index, queue_occupancies in enumerate(max_queue_occs_per_configuration):

			queue_occupancies_without_nan = [ind for ind in queue_occupancies if isinstance(ind, np.int64)]
			queue_occupancies_without_nan = [ind for ind in queue_occupancies if ind != 'nan']
			queue_occupancies_without_nan = [ind for ind in queue_occupancies if isnan(ind) != True]

			maxQueue = max(queue_occupancies_without_nan)


			if len(queue_occupancies) == 0:
				qu_ylim_min.append(0)
				qu_ylim_max.append(0)

			else:
				qu_ylim_min.append(min(queue_occupancies_without_nan))
				qu_ylim_max.append(max(queue_occupancies_without_nan))
>>>>>>> aa8721ca9cec59a980ff7130096e8e59e1fc85a3

		 	hours = hours_per_configuration[index]
			y = np.array(queue_occupancies)
			mask = np.isfinite(np.array(y))
			y_ = np.array(y)[mask]

			line, = axs[i, 1].plot(np.array(hours)[mask], y_, color=colors[index], linestyle='--', lw=0.5)

			axs[i, 1].plot(np.array(hours), y, color=line.get_color(), lw=1)

		###processing average delays##############################################################################3


		delays = get_delays('single', configs_new, args, 'delay_values')
		maxDelay = max(delays)

		x = np.sort(delays)
		y = np.arange(len(delays))/float(len(delays))

<<<<<<< HEAD
def get_embedded_graphs(configs, args):
	overall_best_pdr = []
	overall_max_queue = []

	start_days = args.start_days
	delays = []
	pdrs = []
	queue_occs = []
	maxPDR= 0
	maxQueue=0
	maxDelay = 0

	#to be used for subplots
	fig, axs = plt.subplots(len(start_days), 4)
	i=0

	pdr_xlim_min = []
	pdr_xlim_max = []
	pdr_ylim_max = []
	pdr_ylim_min = []

	qu_ylim_max = []
	qu_ylim_min = []

	for start_day in start_days:

		params_to_extract = {"start-day": start_day}
		configs_new = extract_configs(configs, params_to_extract)

		dataset = get_delivery_ratios('single', configs_new, args, 'pdrvalues')

		axs[i, 0].plot(dataset[0][0], dataset[0][1])
		pdr_xlim_min.append(min(dataset[0][0]))
		pdr_xlim_max.append(max(dataset[0][0]))
		pdr_ylim_min.append(min(dataset[0][1]))
		pdr_ylim_max.append(max(dataset[0][1]))

		maxPDR = max(dataset[0][1])
		hours_per_configuration, max_queue_occs_per_configuration = get_queue_occupancy('single', configs_new, args, 'values')
		overall_best_pdr.append(maxPDR)
		########################process queue occupancies########################################


		endday = get_attribute_value_of_config(configs_new[0], 'end-day')
		overall_max_queue.append(maxQueue)
		for index, queue_occupancies in enumerate(max_queue_occs_per_configuration):

			queue_occupancies_without_nan = [ind for ind in queue_occupancies if isinstance(ind, np.int64)]
			queue_occupancies_without_nan = [ind for ind in queue_occupancies if ind != 'nan']
			queue_occupancies_without_nan = [ind for ind in queue_occupancies if isnan(ind) != True]

			maxQueue = max(queue_occupancies_without_nan)


			if len(queue_occupancies) == 0:
				qu_ylim_min.append(0)
				qu_ylim_max.append(0)

			else:
				qu_ylim_min.append(min(queue_occupancies_without_nan))
				qu_ylim_max.append(max(queue_occupancies_without_nan))

		 	hours = hours_per_configuration[index]
			y = np.array(queue_occupancies)
			mask = np.isfinite(np.array(y))
			y_ = np.array(y)[mask]

			line, = axs[i, 1].plot(np.array(hours)[mask], y_, color=colors[index], linestyle='--', lw=0.5)

			axs[i, 1].plot(np.array(hours), y, color=line.get_color(), lw=1)

		###processing average delays##############################################################################3


		delays = get_delays('single', configs_new, args, 'delay_values')
		maxDelay = max(delays)

		x = np.sort(delays)
		y = np.arange(len(delays))/float(len(delays))

=======
>>>>>>> aa8721ca9cec59a980ff7130096e8e59e1fc85a3
		axs[i, 2].plot(x, y)


		###graphing aggregate stats#####

		values_ = [maxPDR, maxQueue, maxDelay]
		#values_ = [float("{0:.4f}".format(i)) for i in values_	]

		column_names = ['Maximum PDR', "Maximum \nQueue Occupancy", "Maximum Delay"]
		df = pd.DataFrame(np.array(values_).reshape(1,3), columns=column_names)
		the_table = axs[i, 3].table(cellText=df.values, colLabels=df.columns, loc='center', fontsize=20)
		the_table.scale(1.25, 3)
		the_table.auto_set_font_size(False)
		the_table.set_fontsize(8)
		################################
		i+=1

	for x in xrange(i):

		axs[x, 0].axis([min(pdr_xlim_min), max(pdr_xlim_max), min(pdr_ylim_min), max(pdr_ylim_max)])
		axs[x, 0].set_title('PDR')
		axs[x, 0].set_xlabel('Hours')
		axs[x, 0].set_ylabel('Delivery Ratios', fontsize=7)

		axs[x, 1].axis([min(pdr_xlim_min), max(pdr_xlim_max), min(qu_ylim_min), max(qu_ylim_max)])
		axs[x, 1].set_title('Maximum Queue Occupancies')
		axs[x, 1].set_xlabel('Hours')
		axs[x, 1].set_ylabel('Maximum Queue Occupancy',  fontsize=7)

		axs[x, 2].axis([0, max(delays) + 1, 0, 1])
		axs[x, 2].set_title('Average Delay CDF')
		axs[x, 2].set_xlabel('Delays in Hours')
		axs[x, 2].set_ylabel('CDF',  fontsize=7)

		axs[x, 3].set_title('Aggregate Statistics')
		axs[x, 3].axis('off')


	##label the rows
	pad = 3
	position = max(pdr_ylim_max)/float(2)

	rows = ['Start Day {}'.format(row) for row in start_days]
	for ax, row in zip(axs[:,0], rows):
		ax.annotate(row, xy=(0, position), xytext=(-ax.yaxis.labelpad-pad,0),xycoords=ax.yaxis.label, textcoords='offset points', size='medium', ha='right', va='center')

	##title
	configs_content = []
	for f in configs:
		with open(f, 'r') as fi:
			configs_content.append(json.loads(fi.readlines()[0]))

	different, same = get_config_similarity(configs_content)
	title = "Performance metrics for configurations with common values: "

	for key in same:
		title += str(key) + ": " + str(configs_content[0][key]) + ", "

	########################


	fig.suptitle(title, fontsize=9)
	plt.show()

	print "Overall Maximum PDR %d" %(max(overall_best_pdr))
	print "Overall Maximum Queue %d " % (max(overall_max_queue))

def main():

	parser = argparse.ArgumentParser(description='Moby message generation script script.', formatter_class=RawTextHelpFormatter )
	parser.add_argument('--number', help='Number of messages to generate', type=int, nargs='+')
	parser.add_argument('--start-days', help='start day of the year', type=int, nargs='+')
	parser.add_argument('--numdays', help='number of days that the simulation needs to run', type=int, nargs='+')
	parser.add_argument('--configurations', help='Configuration and message file id', type=str, nargs='+')
	parser.add_argument('--city-numbers', help='City to generate messages for', type=int, nargs='+')
	parser.add_argument('--thresholds', help='Minimum occourances to be considered a legit user', type=int, nargs='+')
	parser.add_argument('--cooldowns', help='Cooldown hours, messages distributed over total hours - cooldown hours.', type=int, nargs='+')
	#parser.add_argument('--ttls', help='The time to live to be used for the messages', type=int, nargs='+')
	parser.add_argument('--seeds', help='Number to use for random seeding', type=int, nargs='+')
	parser.add_argument('--queuesizes', help='0 if no queuesize else a specific number with the queuesize value', type=int, nargs='+')
	parser.add_argument('--percentagehoursactive', help='Percentage of hours the destinations stay active', type=int, nargs='+')
	parser.add_argument('--deliveryratiotype', help='1 if total_messages == upto that hour; 2 if total_messages == total number of messages in all hours', type=int, nargs='+')
	parser.add_argument('--messagegenerationtype', help='Original Criteria or Selectively changing sources and destinations', type=int, nargs='+')
	parser.add_argument('--distributiontype', help='2 types -> "uniform" or "user-activity-based" ; used in conjunction with messagegenerationtype', type=str, nargs='+')
	parser.add_argument('--dos-number', help='number of doss', type=int, nargs='+')
	parser.add_argument('--single', help='Use this flag to plot everything on a single plot', action='store_true')
	parser.add_argument('--multiple', help='Use this flag to plot everything on multiple plots', action='store_true')
	parser.add_argument('--useconfigs', help='Use this flag to specify specific configurations to plot', action='store_true')
	parser.add_argument('--foldername', help='Name of the folder with all the results', nargs='?', type=str)
	parser.add_argument('--plottypes', help='Specify plot types. \n 1. get delivery ratio plots' +
																 '\n 2. get queue occupancy plots '
																 '\n 3. get maximum and final delivery ratios' +
																 '\n 4. get maximum queue occupancies' +
																 '\n 5. get average delays in a table' +
																 '\n 6. get minimum and maximum delays' +
																 '\n 7. get heatmaps for each aggregate metric' +
																 '\n 8. get embedded graphs for 3 metrics'

																 , nargs='+', type=int)
	parser.add_argument('--outputfoldername', type=str, nargs='?', required=True)

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

		elif plot == 7:
			get_heatmap(configs, args)

		elif plot == 8:
			get_embedded_graphs(configs, args)

if __name__ == "__main__":
	main()

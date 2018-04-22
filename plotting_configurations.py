from __future__ import division
import pdb
import csv
import matplotlib.pyplot as plt
import subprocess
import numpy as np

def plot_delivery_ratio(foldernames, configtype):

	queuesizes = [i for i in xrange(100,1200,100)]

	for queuesize in queuesizes:
		foldername = [folder for folder in foldernames if '_queuesize_' + str(queuesize) in folder]
		foldername = foldername[0]
		folderpath = str(foldername)
		filename = folderpath + '/' + str(configtype[0]) + '.csv'


		hours = []
		delivery_ratio = []

		with open(filename) as csvfile:
			datareader = csv.reader(csvfile, delimiter=',')
			for row in datareader:
				delivery_ratio.append(int(row[4])/int(row[5]))

		hours = [i for i in xrange(72)]

		plt.plot(hours, delivery_ratio, label=queuesize)
		plt.xlabel('Hours')
		plt.ylabel('Delivery Ratios')
		subprocess.call('mkdir data2/plots', shell=True)
		subprocess.call('mkdir data2/plots/deliveryratioplots', shell=True)

	title = 'Delivery Ratios For Epidemic Routing vs Queue Sizes - Configuration: Message Generation Type ' + str(configtype[0]) + 'DeliveryRatio Type ' + str(configtype[1])

	plt.title(title)
	plt.legend()
        print "Plotting configuration " + str(configtype[0]) + " Delivery Ratio Type " + str(configtype[1])

	plt.savefig('data2/plots/deliveryratioplots/config_' + str(configtype[0]) + '_deliverytype_' + str(configtype[1]))

def plot_queue_occupancies(foldernames, configtype):

	queuesizes = [i for i in xrange(100,1200,100)]

	for queuesize in queuesizes:
		foldername = [folder for folder in foldernames if '_queuesize_' + str(queuesize) in folder]
		foldername = foldername[0]
		folderpath = str(foldername)
		files = subprocess.check_output('ls ' + folderpath, shell=True).split()
		file_ = [f for f in files if 'queue_occupancy' in f]
		file_ = file_[0]
		filename = folderpath + '/' + file_
		queue_occupancy = {}

		for day in xrange(0,3):
			for hour in xrange(0, 24):
				key = str(day) + "," + str(hour)
				queue_occupancy[key] = []



		with open(filename) as csvfile:
			datareader = csv.reader(csvfile, delimiter=',')
			for row in datareader:
				k = row[0] + "," + row[1]
				queue_occupancy[k].append(int(row[3]))

		queue_occupancies = []
		hours = [i for i in xrange(72)]
		max_queue_occs = []
		total = 0
		keys = []

		for key, value in queue_occupancy.iteritems():
                    if len(queue_occupancy[key]) != 0:
                        max_queue_occs.append(np.max(queue_occupancy[key]))
                    else:
                        max_queue_occs.append(0)

		plt.plot(hours, max_queue_occs, label=queuesize)
		plt.xlabel('Hours')
		plt.ylabel('Maximum Queue Occupancies')
		subprocess.call('mkdir data2/plots', shell=True)
		subprocess.call('mkdir data2/plots/queueoccupancyplots', shell=True)

	title = 'Maximum Queue Occupancies For Epidemic Routing vs Queue Sizes - Configuration: Message Generation Type ' + str(configtype[0]) + 'DeliveryRatio Type ' + str(configtype[1])

	plt.title(title)
	plt.legend()
	plt.savefig('data2/plots/queueoccupancyplots/config_' + str(configtype[0]) + '_deliverytype_' + str(configtype[1]))


def get_queue_size_folders(configuration):

	pattern = '_queuesize_*_configuration_' + str(configuration[0]) + '_deliveryratiotype_' + str(configuration[1])
	base_folder = 'data2/results/'
	folders = subprocess.check_output('find ' + base_folder + ' -name "' + pattern + '" ', shell=True)
	folders = folders.split()

	return folders


def main():
	configurations_ = []
	configurations = [0, 1] #defines the .config file; message generation type 0 or 1
	deliveryratiotypes = [1, 2]

	i=0
	for conf in configurations:
		for delrat in deliveryratiotypes:
			configurations_.append([conf, delrat])

	for config in configurations_:
		foldernames = get_queue_size_folders(config)
		plot_delivery_ratio(foldernames, config)
		plot_queue_occupancies(foldernames, config)


if __name__ == "__main__":
	main()

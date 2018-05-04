import pdb
import matplotlib.pyplot as plt
from collections import defaultdict

def main():

	num_messages_uniform = defaultdict(int)
	num_messages_useract = defaultdict(int)
	filename_uniform = '/home/hira/moby_simulator_new/moby_simulator/ExperimentsData/data_1000_queuesize_0_two_distributions_message_generation_1_2/seeds/0_0.config'
	filename_useract = '/home/hira/moby_simulator_new/moby_simulator/ExperimentsData/data_1000_queuesize_0_two_distributions_message_generation_1_2/seeds/0_1.config'
	k=0
	with open(filename_uniform, 'r') as lines:
		for line in lines:
			k += 1
			if k >= 12:
				line = line.strip().split(',')
				num_messages_uniform[line[0]] += 1
	k = 0			
	with open(filename_useract, 'r') as lines:
		for line in lines:
			k += 1
			if k >= 12:
				line = line.strip().split(',')
				num_messages_useract[line[0]] += 1
				 
	hours = [i for i in xrange(60)]

	plt.plot(hours, num_messages_uniform.values(), label='Uniform Distribution')
	plt.plot(hours, num_messages_useract.values(), label='User Activity Based')
	plt.xlabel('Hours', fontsize=7)
	plt.ylabel('Number of Messages', fontsize=7)
	plt.title('Number of Messages Sent Per Hour For Each Message Distribution', fontsize=7)
	plt.legend(fontsize=7, loc='topright')
	plt.show()

if __name__ == "__main__":
	main()

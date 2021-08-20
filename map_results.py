#!/usr/bin/env python3
import argparse
import matplotlib.pyplot as plt
import os
import statistics
import sys
import time

RESULTS_PREFIX = 'data/results/'
REPORTS_PREFIX = 'data/reports/'
RESULT_EXT = '.csv'
MESSAGE_DELAYS_EXT = '_message_delays.csv'
QUEUE_OCCUPANCY_EXT = '_queue_occupancy.csv'

def main():
    parser = argparse.ArgumentParser(description='Moby results visualizer.')
    parser.add_argument('--run-numbers', help='Run number to be plotted.', type=int, nargs='+', default=0)
    parser.add_argument('--quiet', help='Wether to call show or not.', type=bool, nargs='?', default=False)
    parser.add_argument('-p', '--parallelize', help='Whether to parallelize message delay graph generation or not.', type=bool, nargs='?', default=False)
    args = parser.parse_args(sys.argv[1:])
    run_numbers = args.run_numbers
    quiet = args.quiet
    parallelize = args.parallelize
    data_files = {}
    config_ids = {}
    files = os.listdir(RESULTS_PREFIX)
    for run_number in run_numbers:
        data_files[run_number] = []
        for f in files:
            if f.startswith(str(run_number)) and f.endswith(RESULT_EXT) and (not f.endswith(MESSAGE_DELAYS_EXT)) and (not f.endswith(QUEUE_OCCUPANCY_EXT)):
                data_files[run_number].append(f.strip(RESULT_EXT))
        data_files[run_number].sort(key=lambda x: int(x.split('_')[-1].strip(RESULT_EXT)))
        config_ids[run_number] = [int(i.split('_')[-1].strip(RESULT_EXT)) for i in data_files[run_number]]
    data_file_keys = list(data_files.keys())
    # Check if all run number have the same number of simulations
    assert all(config_ids[x] == config_ids[data_file_keys[0]] for x in data_file_keys)
    ratios = {}
    for run_number in data_file_keys:
        ratios[run_number] = []
        filtered_files = data_files[run_number]
        for f in filtered_files:
            with open(RESULTS_PREFIX + f + RESULT_EXT, 'r') as infile:
                last = infile.readlines()[-1]
                last = last.split(',')
                delivered = last[3]
                total = last[4]
                ratios[run_number].append(float(delivered) / float(total))
    means = []
    deviations = []
    for i in config_ids[data_file_keys[0]]:
        vals = [ratios[j][i] for j in data_file_keys]
        means.append(statistics.mean(vals))
        deviations.append(statistics.stdev(vals))
    print(means, deviations)
    print("Plotting results for:", run_numbers)
    plt.figure(figsize=(16,9))
    plt.style.use('ggplot')
    plt.title('Results seen for run number ' + str(run_numbers) + ' Configurations: ' + str(len(filtered_files)))
    plt.xlabel('Configuration ID')
    plt.ylabel('Delivery Ratio at the end of the simulation')
    xaxis = [i for i in range(0, len(config_ids[data_file_keys[0]]))]
    plt.errorbar(xaxis, means, yerr=deviations, fmt='o', ecolor='b', capsize=5)
    plt.xticks(rotation=45)
    plt.xticks(xaxis, config_ids[data_file_keys[0]])
    report_id = str(run_numbers[0])
    for rn in run_numbers[1:]:
        report_id += "_" + str(rn)
    REPORT_DIR = REPORTS_PREFIX + report_id + "/"
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
    plt.savefig(REPORT_DIR + "delivery_ratios.eps", format="eps", dpi=1200)
    if not quiet:
        plt.show()
    plt.gcf().clear()
    for rn in run_numbers:
        print("Launching plot message delays for", rn)
        for f in data_files[rn]:
            if(parallelize):
                os.system("./plot_message_delays.py --quiet True --run-number " + f + " &")
            else:
                os.system("./plot_message_delays.py --quiet True --run-number " + f)
        time.sleep(10)

if __name__ == "__main__":
    main()

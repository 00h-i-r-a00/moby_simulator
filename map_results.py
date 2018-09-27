#!/usr/bin/env python3
import argparse
import matplotlib.pyplot as plt
import os
import sys

RESULTS_PREFIX = 'data/results/'
REPORTS_PREFIX = 'data/reports/'
RESULT_EXT = '.csv'
MESSAGE_DELAYS_EXT = '_message_delays.csv'
QUEUE_OCCUPANCY_EXT = '_queue_occupancy.csv'

def main():
    parser = argparse.ArgumentParser(description='Moby results visualizer.')
    parser.add_argument('--run-number', help='Run number to be plotted.', type=int, nargs='?', default=0)
    parser.add_argument('--quiet', help='Wether to call show or not.', type=bool, nargs='?', default=False)
    args = parser.parse_args(sys.argv[1:])
    run_number = args.run_number
    quiet = args.quiet
    files = os.listdir(RESULTS_PREFIX)
    filtered_files = []
    for f in files:
        if f.startswith(str(run_number)) and f.endswith(RESULT_EXT) and (not f.endswith(MESSAGE_DELAYS_EXT)) and (not f.endswith(QUEUE_OCCUPANCY_EXT)):
            filtered_files.append(f.strip(RESULT_EXT))
    filtered_files.sort(key=lambda x: int(x.split('_')[-1].strip(RESULT_EXT)))
    config_ids = [i.split('_')[-1].strip(RESULT_EXT) for i in filtered_files]
    print("Plotting results for:", filtered_files)
    ratios = []
    for f in filtered_files:
        with open(RESULTS_PREFIX + f + RESULT_EXT, 'r') as infile:
            last = infile.readlines()[-1]
            last = last.split(',')
            delivered = last[-2]
            total = last[-1]
            ratios.append(float(delivered) / float(total))
    plt.figure(figsize=(16,9))
    plt.style.use('ggplot')
    plt.title('Results seen for run number ' + str(run_number) + ' Configurations: ' + str(len(filtered_files)))
    plt.xlabel('Configuration ID')
    plt.ylabel('Delivery Ratio at the end of the simulation')
    xaxis = [i for i in range(0, len(config_ids))]
    plt.plot(xaxis, ratios, marker='o')
    plt.xticks(rotation=45)
    plt.xticks(xaxis, config_ids)
    REPORT_DIR = REPORTS_PREFIX + str(run_number) + "/"
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
    plt.savefig(REPORT_DIR + "delivery_ratios.eps", format="eps", dpi=1200)
    if not quiet:
        plt.show()
    plt.gcf().clear()
    for f in filtered_files:
        os.system("./plot_message_delays.py --quiet True --run-number " + f)

if __name__ == "__main__":
    main()

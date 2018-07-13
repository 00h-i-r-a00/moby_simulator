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
def plot_delivery_ratio(plot_number, configs, args):
    
    ###create a folder if it doesn't already exist
    
    
    ##############################################
    ##configs conts filepaths to configs
    configs_content = []
    dataset = []
    #if single
    if plot_number[0]:
        for f in configs:
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
    
    for key in configs_content[0].keys():
        x = []
        for config in configs_content:
            x.append(config[key])
        x = set(x)    
        if len(x) != 1:
            config_different_key_values.append(key)
        else:
            config_same_key_values.append(key)
        


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
    title = ''

    for key in config_same_key_values:
        title += key + ': ' + str(configs_content[0][key]) + '; '

    title = 'Delivery Ratio Vs Hour \n Configuration: ' + title
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.title(title, fontsize=9)
    plt.xlabel('Hours', fontsize=9)
    plt.ylabel('Delivery Ratio', fontsize=9)
    figname = 'dummy_'
    figname = figname + '_deliveryratio.png'
    plt.savefig(figname)
        
        
    
def plot_queue_occupancy(plot_number, configs, args):   
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
            
    for filename in queue_occupancy_files:
        queue_occupancy = {}
        ##initialization
        for day in xrange(args.start_days[0],args.start_days[0] + 3):
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
                print exc                   
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
                    print exc
                                    
    
        legend = ''
    
        for key in config_different_key_values:
            legend += ' ' + key + ':' + str(configs_content[p][key])

    
        plt.xticks(fontsize=7)
        plt.yticks(fontsize=7)
        y = np.array(max_queue_occs)
        mask = np.isfinite(np.array(y))
    
        num_nan.append(len([i for i in mask if i == False]))
    
        y_ = np.array(y)[mask]
    
        line, = plt.plot(np.array(hours)[mask], y_,label=legend, color=colors[p], linestyle='--', lw=0.5)
        plt.plot(np.array(hours), y,label=legend, color=line.get_color(), lw=1)

        plt.legend(fontsize=7,  bbox_to_anchor=(1.1, 1.05))
        p +=1 
    
    title = ''
    for key in config_same_key_values:
        title += key + ': ' + str(configs_content[0][key]) + '; '

    plt.title(title, fontsize=7)
    figname = 'dummy_'
    figname = figname + '_queuecoccupancy.png'
    plt.savefig(figname)
    
def plot_active_users(start_day, end_day):
    pass
    
def get_maximum_delivery_ratios(plot_number, configs, args):
    pass
    #for each config
    #read all the delivery ratios, get the maximum
    
def get_maximum_queue_occupancies(plot_number, configs):
    pass
    ##for each config
    ##read all the queue occupancies, get the maximum

def get_average_delays(plot_number, configs, args):
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
    fig, ax = plt.subplots()
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')

    fig.tight_layout()

    colLabels = ['Configuration Name', 'Average Delay']
    the_table = ax.table(cellText=cellText, colLabels=colLabels, loc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(10)
    the_table.scale(1, 5)
    #the_table.set_title('Table')
    
    plt.savefig('1000messages.png')            
    
    title = ''
    for key in config_same_key_values:
		title += str(key) + ': ' + str(configs_content[0][key]) + "; "
    
    print title
    
def get_configs(args):
    number_of_messages = args.number
    start_days = args.start_days
    number_of_days = [3]
    
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
    
    parser = argparse.ArgumentParser(description='Moby message generation script script.')
    parser.add_argument('--number', help='Number of messages to generate', type=int, nargs='+')
    parser.add_argument('--start-days', help='start day of the year', type=int, nargs='+')
    parser.add_argument('--end-day', help='end day of the year', type=int, nargs='+')
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
    parser.add_argument('--single', help='Use this flag to plot everything on a single plot', action='store_true')
    parser.add_argument('--multiple', help='Use this flag to plot everything on multiple plots', action='store_true')
    parser.add_argument('--useconfigs', help='Use this flag to specify specific configurations to plot', action='store_true')
    parser.add_argument('--plottypes', help='Specify plot types', nargs='+', type=int)
    parser.add_argument('--foldername', help='Name of the folder with all the results', nargs='?', type=str)
    
    args = parser.parse_args(sys.argv[1:])
    print args
    
    useconfigs = args.useconfigs
    plottypes = args.plottypes
    
    if useconfigs:
        #contains the paths of all the configs to plot  
        configs = [os.getcwd() + '/' + args.foldername + '/configs/' + f for f in args.configurations]
    
    else:
        #contains the paths of all the configs to plot
        configs = get_configs(args)
    
        
    plot_functions = {
                      1: plot_delivery_ratio, 
                      2: plot_queue_occupancy, 
                      3: get_maximum_delivery_ratios,
                      4: get_maximum_queue_occupancies,
                      5: get_average_delays
                      }
                            
    for plot in plottypes:
        plot_number = (args.single, args.multiple)
        plot_functions[plot](plot_number, configs, args)
        
            
if __name__ == "__main__":
    main()

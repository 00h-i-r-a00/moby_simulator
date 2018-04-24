#!/usr/bin/env python
import sys
import matplotlib.pyplot as plt
import pdb
import json
import os
print "Running"
plt.xlabel('Hours')
plt.ylabel('Delivery Ratio')
dataset = []
configs = []
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
            delivery_ratio.append(float(message_delivery_count)/int(total_messages))
    
    
    config_filename = os.getcwd() + '/configs/' + f.split('/')[2].split('.')[0] + '.txt'
    with open(config_filename, 'r') as f:
        configs.append(json.loads(f.readlines()[0]))
    
    dataset.append((hour_list, delivery_ratio))

config_different_key_values = []
config_same_key_values = []
for key in configs[0].keys():
    x = []
    for config in configs:
        x.append(config[key])
    x = set(x)    
    if len(x) != 1:
         config_different_key_values.append(key)
    else:
        config_same_key_values.append(key)

print "Plotting", dataset
i=0
for data in dataset:
    #for the corresponding config, get the values corresponding to the
    #keys that are different, and store it in legend
    legend = ''
    for key in config_different_key_values:
        legend += ' ' + key + ':' + str(configs[i][key])

    i +=1 
    
    plt.plot(data[0], data[1], marker='o', label=legend)
    plt.legend()
title = ''
for key in config_same_key_values:
    title += key + ': ' + str(configs[0][key]) + '; '

title = 'Delivery Ratio Vs Hour for config: ' + title
plt.title(title)
plt.show()

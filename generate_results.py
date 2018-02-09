#!/usr/bin/env python
import sys
import matplotlib.pyplot as plt

print "Running"
plt.xlabel('Hours')
plt.ylabel('Delivery Ratio')
dataset = []
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
    dataset.append((hour_list, delivery_ratio))
print "Plotting", dataset
for data in dataset:
    plt.plot(data[0], data[1], marker='o')
plt.show()

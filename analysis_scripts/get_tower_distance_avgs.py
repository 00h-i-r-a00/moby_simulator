#!/usr/bin/env python3
import sys
import math
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
plt.style.use('seaborn-whitegrid')

def main():
    if len(sys.argv) <= 1:
        print("Input towers file as cli arg...")
    infile = sys.argv[1]
    towers = {}
    distances = defaultdict(list)
    zeros = 0
    nonzeros = 0
    with open(infile, "r") as inf:
        line = inf.readline()
        while line:
            id, lat, lon, _ = line.strip().split(" ")
            towers[id] = (float(lat), float(lon))
            line = inf.readline()
    x = []
    y = []
    x_abs = []
    y_abs = []
    # Madrid
    x_normal = 40.383333
    y_normal = -3.716667
    for t in towers:
        x1, y1 = towers[t]
        x_abs.append(x1)
        y_abs.append(y1)
        x1 -= x_normal
        y1 -= y_normal
        x.append(x1)
        y.append(y1)
    # print(x, y)
    print("X min, max", min(x_abs), max(x_abs))
    print("Y min, max", min(y_abs), max(y_abs))
    """
    plt.plot(x, y, 'o', color='black');
    plt.show();
    plt.savefig("tower_map.png")#, transparent=True)
    plt.close()
    """
    for t1 in towers:
        lat1, lon1 = towers[t1]
        for t2 in towers:
            if t1 == t2:
                continue
            lat2, lon2 = towers[t2]
            dist = math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)
            distances[t1].append(dist)

    avg_over = 5
    non_zero_avgs = []
    with_zero_avgs = []
    for t1 in towers:
        t1_dist = get_first_n(avg_over, True, distances[t1])
        non_zero_avgs.append(sum(t1_dist) / avg_over)
    for t1 in towers:
        t1_dist = get_first_n(avg_over, False, distances[t1])
        with_zero_avgs.append(sum(t1_dist) / avg_over)

    print("Mean without zeros:", np.average(non_zero_avgs), np.std(non_zero_avgs))
    print("Mean with zeros:", np.average(with_zero_avgs), np.std(with_zero_avgs))

    print("Zeros:", zeros, "Nonzeros:", nonzeros)

def get_first_n(number, drop_zeros, distance_list):
    ret_lst = []
    sorted_dist = sorted(distance_list)
    pointer = 0
    while len(ret_lst) < 5:
        if drop_zeros and sorted_dist[pointer] == 0:
            pointer += 1
        else:
            ret_lst.append(sorted_dist[pointer])
            pointer += 1
    return ret_lst

if __name__ == "__main__":
    main()

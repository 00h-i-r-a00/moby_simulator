#!/usr/bin/env python
import sys
import argparse
import matplotlib.pyplot as plt
from collections import defaultdict

DATA_FILE_PREFIX = "data/"
DATA_FILE_FORMAT = ".twr"

def main():
    plt.xlabel('Number of times seen.')
    plt.ylabel('Number of users.')
    dataset = []
    userpool = defaultdict(int)
    parser = argparse.ArgumentParser(description='Moby message generation script script.')
    parser.add_argument('--number', help='Number of days to consider', type=int, nargs='?', default=3)
    parser.add_argument('--start-day', help='start day of the year', type=int, nargs='?', default=0)
    parser.add_argument('--city-number', help='City to generate messages for', type=int, nargs='?', default=0)
    args = parser.parse_args(sys.argv[1:])
    start_day = args.start_day
    number_of_days = args.number
    city = args.city_number
    for current_day in xrange(start_day, start_day+number_of_days):
        for current_hour in xrange(0, 24):
            current_data_file =  DATA_FILE_PREFIX + str(city) + "/" + str(current_day) + "_" + str(current_hour) + DATA_FILE_FORMAT
            users_this_hour = []
            with open(current_data_file) as data:
                for entry in data:
                    hour, tower_id, user_ids = entry.split(",")
                    user_ids = user_ids.strip()
                    users_this_hour += user_ids.split("|")
            users_this_hour = set(users_this_hour)
            for u in users_this_hour:
                userpool[u] += 1
    freq_freq = defaultdict(int)
    for key, value in userpool.iteritems():
        freq_freq[value] += 1
    x = []
    y = []
    total_users = len(userpool.keys())
    for key, value in sorted(freq_freq.iteritems(), key=lambda(k,v): (v,k)):
        x.append(key)
        y.append(value)
    print x, y
    plot = plt.bar(x, y)
    plt.title("Total users " + str(total_users) + " seen between days " + str(start_day) + " and " + str(start_day + number_of_days))
    rects = plot.patches
    for rect, label in zip(rects, y):
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2, height + 5, label, ha='center', va='bottom', rotation=45)
    plt.show()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

RESULTS_PREFIX = 'data/results/'
RESULT_EXT = '.csv'
ttls = [12, 24, 36, 48, 60, 72]
#distributiontype = ['region_sms_based']
thresholds = [4]
#infinite since we are intially taking an estimate of the possible PDRs
dos_numbers = [0, 2, 4, 6, 8, 10]
rn = "2019011614353"
rn = "20190118171136"

def main():
    ctr = 0
    print("Time To Live, Threshold, DoS Number, Delivered Messages, Total Messages")
    for ttl in ttls:
        for threshold in thresholds:
            for dos_number in dos_numbers:
                f = rn + "_" + str(ctr)
                ctr += 1
                with open(RESULTS_PREFIX + f + RESULT_EXT, 'r') as infile:
                    last = infile.readlines()[-1]
                    last = last.split(',')
                    delivered = last[-2]
                    total = last[-1].replace('\n', '')
                    print(getline(ttl, threshold, dos_number, delivered, total, "trust"))

def getline(*args):
    retstr = str(args[0])
    dlim = ','
    for i in args[1:]:
        retstr = retstr + dlim + str(i)
    return retstr


if __name__ == "__main__":
    main()

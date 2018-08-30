import os
import sys

def main():
    if len(sys.argv) != 2:
        print "Usage: python check_completed_simulations.py foldername"
        sys.exit()

    path = os.getcwd() + '/' + sys.argv[1] + '/logs/'
    import pdb
    files = os.listdir(path)
    files = [f for f in files if 'achtung' not in f]
    sim_done = 0
    sim_done_list = []

    not_done = []

    for fi_ in files:
        with open(path + fi_, 'r') as f:
            lines = f.readlines()
            lastline = '' if not lines else lines[-1]

            if 'Simulation Done' in lastline:
                sim_done += 1
                sim_done_list.append(fi_.replace('.nohup', '.txt'))

            else:
				not_done.append(fi_.replace('.nohup', '.txt'))

    all_configs = []
    configs_path = os.getcwd() + '/' + sys.argv[1] + '/configs/'
    config_files = os.listdir(configs_path)

    uncompleted_configs = set(config_files).difference(set(sim_done_list))
    print "Number of Completed Sims: %d" %(sim_done)
    print "Number of UnCompleted Sims: (Include Sims with partial nohups (if any)): %d" %(len(uncompleted_configs))
    print "Number of UnCompleted Sims with Partial nohups (need to be investigated): %d" % (len(not_done))

    print "UnCompleted Configs:"

    for conf in uncompleted_configs:
        print conf

    print "Uncomplted Configs With Partial Nohup:"

    for conf in not_done:
        print conf

if __name__ == "__main__":
    main()

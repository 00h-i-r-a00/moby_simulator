import os

def main():

    path = os.getcwd() + '/data/logs/'
    files = os.listdir(path)

    simulations_done = []
    for fi_ in files:
        with open(path + fi_, 'r') as lines:
            for line in lines:
                if "Simulation Done" in line:
                    print(fi_.replace('.nohup', ''))


if __name__ == "__main__":
    main()

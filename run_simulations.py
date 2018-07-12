#!/usr/bin/env python
import socket, json
import os

def main():
    hostname = socket.gethostname()
    print hostname
    with open (hostname+".json") as configs:
        confs = configs.readline().strip().split("!")
        confs = confs[1:]
    for conf in confs:
        cnf = json.loads(conf)
        msg_gen_string = "./generate_messages.py "
        for key, value in cnf.iteritems():
            if key == 'usethreshold':
                if value == True:
                    msg_gen_string += "--" + key + " "
            else:        
                msg_gen_string += "--" + key + " " + str(value) + " "
        print msg_gen_string
        os.system(msg_gen_string)
        print cnf
        cnf_id = str(cnf["configuration"])
        os.system("nohup ./moby_simulator.py --configuration " + cnf_id + " > data/logs/"+ cnf_id+".nohup" +"&")

if __name__ == "__main__":
    main()

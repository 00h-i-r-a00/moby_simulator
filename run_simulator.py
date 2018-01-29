import os
import sys
import pdb
import argeparse

#scripts that automatically collect all the data

class User(object):
    
    def __init__ (self, userID, tower, contacts, priority_queue, besteffort_queue, message) 
        #why initialize the users with the priority_queue and the best_effort queue --> going to be empty initially?
#TODO: understand how priority and best effort queues work
        #set initial tower
        self.userID = userID
        self.tower = tower
        self.priority_queue = priority_queue #initialize
        self.besteffort_queue = besteffort_queue #initialize
        #TODO: what is the queue going to be, how to structure the queue and put messages in and out
        self.contacts = contacts
        self.trust_scores = #intially null
        self.message = message

    def set_location(self, hour):
        pass
        #check the tower the user is connected to in that hour -> user -> hour -> tower mappings
        #update tower
    def get_location(self, hour):
        pass

    def update_message_queue(self):
        pass

    def set_trustscores(self, user)
        #extract trust scores for that user
        pass

    def send_message(message):
        #send message to all towers connected to the users based on the trust queue


class NetworkState(object):
    pass

class Statistics(object):
    
    def __init__ (self):
        pass

    def update_total_unique_message_received():
        pass

#TODO: figure out whether global variables are fine or statistics needs to have its own class
#TODO: how to use the statistics class to have statistics

#        pass
#
#    def update_stats(self, message_transferred, message_dropped)

#class Message(object)

 #   def __init__(self, src, dst, number_of_hops, message):
  #      self.src = src
   #     self.dst = dst
    #    self.number_of_hops = 0
     #   self.message = message
       

    #def update_message(self, src, dst):
     #   self.src = src
       # self.dst = dst
       # self.number_of_hops = number_of_hops
        #update number of hops
        #check TTL
        #check if message has reached destination
        ##how to update a global class that computes statistics

      
      
def get_users_connected_to_tower_a_particular_hour(tower, hour):
    pass       
     
def get_all_users_connected_to_towers(towers):
    pass

def get_all_towers_within_region():
    #currently make a static file and read that to get a list of all the towers that I am interested in
    #this would theoretically involve me giving the co-ordinates of the geographic region, then mapping all 
    #the towers to that location
    ##TODO: get this file
def get_all_towers_within_hour(hour):
    pass

def initialize_source_destinations():
    pass

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', action='store', dest='total_time_for_simulation', help='Overall time you need the simulation to run (in hours)')
    
    results = parser.parse_args()

    #instantiate the Statistics class; make it global later

    total_hours = int(results.total_time_for_simulation)
    src_dst_list = initialize_source_destinations() #contains tuples of all the randomly chosen sender/receiver pairs in the simulation
    num_users = #total number of users in the simulation; total number of users I choose to simulate

   #TODO####initialize all the users
    for i in xrange(num_users):

        #initialize each user with its id, tower, empty queues, contacts, precomputed trust scores, and fixed message
        #TODO: toask: assuming that these users are randomly chosen (any tower); how many users overall -> get these users from the list of total users?
        #TODO: toask: initialize all of the users from their location; what happens if these users do not exist in the current location 
        ## TODO: get the user, tower mappings for every hour

    ##running the simulation

    for hour in total_hours:
        tower = get_all_towers_within_hour(hour)
        for tower in total_towers:
            users = get_users_connected_to_tower_in_a_particular_hour(tower, hour)
            for user in users:
                #check if user is present in any one of the src_dst pairs that I have
                #if yes:
                    #send message
                    ##########################sending message#############################
                    #1. update message queue of the user based on the trust scores it has with its contacts
                    #2. broadcast messages based on the trust scores and all TODO: figure this out; what happens over here
                    # some messages get sent to the receivers, some get dropped
                    #3. update message queues of the receiver
                    #4. decrement the number of hops in the message itself
                    #5. update the Statistics class; dropped messages; messages received
                    ######################################################################
                    #TODO: send to all receivers connected to this user, update receiver queues
     
            #a) check whether the message was intended for the receiver, if yes, update statistics; if no increment number of hops and update the queues
            #TODO: when updating the queues, do I send from the receiver at the same time too?
            
            
                      
            #select random users connected to the tower (as senders)
            #all other users in the same tower are receivers
            #send message from the user; sending message involves keeping track of the message the user is sending which means that I need to know that this particular user sent a message in this particular hour 
            #check whether the user has any queue to send

        #TODO For 29th January -> figure out the trust protocol; implement the rest of the stuff










if __name__ == "__main__":
    main()


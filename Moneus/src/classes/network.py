
import json


class Network:

    zeros = 21
    delay = 1
    miners_reward = 3
    streams = []
    hosts = []
    blockchain = {} 

    def __init__(self):
        self.peers = []
        self.miners = []
        self.users = []

    def show(self):
        print("BlochChain:", self.blockchain)
        print("Peers:", self.peers)
        print("Miners:", self.miners)
        print("Users:", self.users)

    def output(self, what_to_output):
        
        if what_to_output == "U":

            for i in self.users:
                i.show()
        
        elif what_to_output == "M":
            
            for i in self.miners:
                i.show()

        elif what_to_output == "P":
            for i in self.peers:
                i.show()

    def broadcast_message(self, json_dict_message, hosts):
    
        str_msg = str(json_dict_message) #
        len_str_msg = len(str_msg)
        str_len_str_msg = str(len_str_msg) #
        len_str_len_str_msg = len(str_len_str_msg)
        str_len_str_len_str_msg = str(len_str_len_str_msg)#
        message = str_len_str_len_str_msg + str_len_str_msg + str_msg
        d = message
        msg = json.dumps(d)
        msg = bytes(msg, 'utf-8')
        for i in hosts:
            i.send(msg)
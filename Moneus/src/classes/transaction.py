
import json
from objects import main_network
from network import Network


class Transaction:
    
    def __init__(self, sender, receiver, amount, signature):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature

    def show(self):
        print(self.sender)
        print(self.receiver)
        print(self.amount)
        print(self.signature)

    def send(self):

        #writes the transaction data and the signature on JSON file
        transaction = {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "signature": self.signature
            }
        
        with open('transaction.json', 'r+') as json_file:
           
            #file_data = json.load(json_file)
            json_file.seek(0)  
            json_file.truncate() 
            json.dump(transaction, json_file, indent=4)

        main_network.broadcast_message(transaction, main_network.hosts)
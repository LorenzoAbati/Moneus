
import json
from os import getlogin
import time
import hashlib

from peer import Peer
from block import Block
from objects import handyman
from transaction import Transaction
from objects import main_network
import firebase.database_services as firebase_services


class Miner(Peer):

    global mining
    mining = True
    name = ""

    def __init__(self, email, secret_key, public_key, wallet, hashrate, is_miner):
        super().__init__(email, secret_key, public_key, wallet)

        self.hashrate = hashrate
        self.is_miner = is_miner

    def show(self):
        
        super().show()
        print("hashrate:",self.hashrate)
        print("is_miner:",self.is_miner)

    def check_hash(self, bin_data):

        for i in range(0, main_network.zeros):

            if bin_data[i] != "0":
                return "nann"

        return bin_data

    def get_prev_hash(self):

        with open('src.json') as blockchain_file:
            blockchain_data = json.load(blockchain_file)

        block_number = handyman.get_number_of_blocks(blockchain_data)

        #blockchain_data = blockchain_data.items()
        for value in blockchain_data.items():
            if value[0] == str(block_number-1):
                prev_hash = value[1][0]['hash']
                 
        return prev_hash, block_number

    def mine(self, transaction): 
        global mining
        mining = True

        pow = 0
        prev_hash, number = self.get_prev_hash()
        reward = main_network.miners_reward
        miner = self.wallet.address

        sender = transaction["sender"]
        receiver = transaction["receiver"]
        amount = transaction["amount"]
        signature = transaction["signature"]

        self.write_on_logs("mining...")
        self.set_status("MINING")

        while mining:
            pow += 1
            raw_block = prev_hash + sender + receiver + amount + str(reward) + miner + signature + str(pow)
            value_to_hash = raw_block

            loshex = hashlib.sha256((str(value_to_hash)).encode('utf-8')).hexdigest()
            bin_data = bin(int(loshex, 16))[3:]

            if len(self.check_hash(bin_data)) == 255: 

                self.write_on_logs("done")
                self.set_status("STOPPED")
                transaction = Transaction(sender, receiver, amount, signature)
                block = Block(number, prev_hash, transaction, reward, miner, str(pow), bin_data) #add number
                block.write_in_blockchain()
                
                break

        if mining == False:

            self.write_on_logs("I STOPPED MINING")

    def read_block_from_blockchain(self,blockchain):
        
        blockchain_data = blockchain

        blocks_number = handyman.get_number_of_blocks(blockchain)

        for block_data in blockchain_data.items():
           
            if block_data[0] == str(blocks_number-1):
                prev_hash = block_data[1][0]["prev_hash"]
                sender = block_data[1][0]["transaction"][0]["sender"]
                receiver = block_data[1][0]["transaction"][0]["receiver"]
                amount = block_data[1][0]["transaction"][0]["amount"]
                signature = block_data[1][0]["transaction"][0]["signature"]
                reward = block_data[1][0]["reward"]
                miner = block_data[1][0]["miner"]
                pow = block_data[1][0]["proof_of_work"]
                hash = block_data[1][0]["hash"]
        
        return prev_hash, sender, receiver, amount, signature, reward, miner, pow, hash
        
    def verify_last_block(self,blockchain):

        block_data = self.read_block_from_blockchain(blockchain)

        prev_hash = block_data[0]
        sender = block_data[1]
        receiver = block_data[2]
        amount = block_data[3]
        signature = block_data[4]
        reward = block_data[5]
        miner = block_data[6]
        pow = str(block_data[7])

        raw_block = prev_hash + sender + receiver + amount + str(main_network.miners_reward) + miner + signature + str(pow)

        loshex = hashlib.sha256((str(raw_block)).encode('utf-8')).hexdigest()
        bin_data = bin(int(loshex, 16))[3:]

        if len(self.check_hash(bin_data)) == 255: 
            return True
        else:
            return False

    def verify_blockchain(self, blockchain_data):

        senders = []
        receivers = []
        hashes = []
        prev_hashes = []

        for block_data in blockchain_data.items():
            
            prev_hash = block_data[1][0]["prev_hash"]
            sender = block_data[1][0]["transaction"][0]["sender"]
            receiver = block_data[1][0]["transaction"][0]["receiver"]
            amount = block_data[1][0]["transaction"][0]["amount"]
            signature = block_data[1][0]["transaction"][0]["signature"]
            reward = block_data[1][0]["reward"]
            miner = block_data[1][0]["miner"]
            pow = block_data[1][0]["proof_of_work"]
            hash = block_data[1][0]["hash"]

            if sender in senders:
                index = senders.index(sender)
                senders[index+1] += float(amount)
            else:
                senders.append(sender)
                senders.append(float(amount))

            if receiver in receivers:
                index = receivers.index(receiver)
                receivers[index+1] += float(amount)
            else:
                receivers.append(receiver)
                receivers.append(float(amount))

            if miner in receivers:
                index = receivers.index(miner)
                receivers[index+1] += float(reward)
            else:
                receivers.append(miner)
                receivers.append(float(reward))

        counter = 0
       
        for i in senders:
            
            if counter%2 == 0:
                if i in receivers:
                    k = receivers.index(i)

                    if senders[senders.index(i)+1] > receivers[k+1]:
                        self.write_on_logs("false transaction")
                        return False
                    else:
                        self.write_on_logs("transactions are ok")
                        

                elif senders[senders.index(i)+1] == 0:
                    self.write_on_logs("transactions are ok")

                elif type(i) != float:
                    self.write_on_logs("false transaction")
                    return False

            counter += 1

        if self.verify_last_block(blockchain_data) == False:
            self.write_on_logs("false transaction")
            return False

        for block_data in blockchain_data.items():

            hash = block_data[1][0]["hash"]
            prev_hash = block_data[1][0]["prev_hash"]
            hashes.append(hash)
            prev_hashes.append(prev_hash)

        n_blocks = handyman.get_number_of_blocks(blockchain_data)

        for i in range(n_blocks-1):
            if hashes[i] != prev_hashes[i+1]:
                self.write_on_logs("false transaction")
                return False

        self.write_on_logs("MINER src is legit!")
        return True
            

    def verify_transaction(self,transaction):

        str_publick_key = firebase_services.get_public_key(transaction["sender"])
        public_key = handyman.public_key_hex_string_to_object(str_publick_key)
        transaction_data = str(transaction["sender"]) + str(transaction["receiver"]) + str(transaction["amount"])
        transaction_data = transaction_data.encode()
        
        return handyman.verify(transaction["signature"], transaction_data, public_key)

    def show_transactions(self):
        super().show_transactions()

    def stop_mining(self):
        global mining 
        mining = False

    def write_on_logs(self,message):
        super().write_on_logs(message)

    def set_status(self, status):
        firebase_services.set_miner_status(self.wallet.address, status)

    def get_status(self):
        return firebase_services.get_miner_status(self.wallet.address)
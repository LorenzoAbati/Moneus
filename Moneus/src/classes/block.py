
import json
from objects import main_network


class Block:
    
    def __init__(self, number, prev_hash, transaction, reward, miner, pow, hash): #pow = proof of work
        self.number = number
        self.prev_hash = prev_hash
        self.transaction = transaction 
        self.reward = str(reward)
        self.miner = miner
        self.pow = pow
        self.hash = hash
    
    def show(self):
        print("number:",self.number)
        print("prev hash:",self.prev_hash)
        print("transaction")
        print(" sender:",self.transaction.sender)
        print(" receiver:",self.transaction.receiver)
        print(" amount:",self.transaction.amount)
        print(" signature:",self.transaction.signature)
        print("reward:",self.reward)
        print("miner:",self.miner)
        print("proof of work:",self.pow)
        print("hash:",self.hash)

    def write_in_blockchain(self):

        block = {
            str(self.number): [
                {
                "prev_hash": self.prev_hash,
                "transaction":[{
                    "sender":self.transaction.sender,
                    "receiver":self.transaction.receiver,
                    "amount":self.transaction.amount,
                    "signature":self.transaction.signature
                    }],
                "miner": self.miner,
                "reward": self.reward,
                "proof_of_work": self.pow,
                "hash": self.hash
            }],
        }

        main_network.blockchain.update(block)

        try:
            with open('src.json', 'r+') as blockchain_file:
                file_data = json.load(blockchain_file)
                file_data.update(block)
                blockchain_file.seek(0)
                json.dump(file_data, blockchain_file, indent = 4)
 
            return 0 #success
        except:
            return 1 #error

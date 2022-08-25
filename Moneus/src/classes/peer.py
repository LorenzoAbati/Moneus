
import json
from os import name

from objects import handyman
from objects import main_network

from transaction import Transaction

import firebase.authentication as firebase_authentication
import firebase.database_services as firebase_services


class Peer:

    name = ""

    def __init__(self, email, secret_key, public_key, wallet):
        self.email = email
        self.secret_key = secret_key
        self.public_key = public_key
        self.wallet = wallet
        self.transactions = []
    
    def show(self):
        print("email:",self.email,", id(sha1):",handyman.hash_email(self.email))
        try:
            print("secret key:",self.secret_key.as_hex())
            print("public key:",self.public_key.as_hex())
        except:
            print("secret key:",self.secret_key)
            print("public key:",self.public_key)
        print("wallet")
        print(" address:",self.wallet.address)
        print(" money:",self.wallet.money)
        
    def read_transaction(self):

        with open('transaction.json') as transaction_file:
            transaction_data = json.load(transaction_file)
    
        sender = transaction_data["sender"]
        receiver = transaction_data["receiver"]
        amount = transaction_data["amount"]
        signature = transaction_data["signature"]
        
        return sender, receiver, amount, signature

    def verify_transaction(self): #in teoria non serve oerche lo fa il miner
    
        transaction_data = self.read_transaction()

        transaction = str(transaction_data[0]) + str(transaction_data[1]) + str(transaction_data[2])
        transaction = transaction.encode()
        signature = transaction_data[3]

        return handyman.verify(signature, transaction, self.public_key)
        
    def send_money_to(self, receiver_wallet_address, amount):
    
        if self.wallet.money >= amount:
            transaction_data = str(self.wallet.address) + receiver_wallet_address + str(amount)
            transaction_data = transaction_data.encode()

            signature = handyman.sign(transaction_data, self.secret_key)
            transaction = Transaction(str(self.wallet.address), receiver_wallet_address, str(amount), signature)
            
            transaction.send()

            return 0

        else:
            
            return 1

    def count_money(self):

        money_amount = 0
    
        blockchain = main_network.blockchain

        for block_data in blockchain.items():
            
            sender = block_data[1][0]["transaction"][0]["sender"]
            receiver = block_data[1][0]["transaction"][0]["receiver"]
            amount = block_data[1][0]["transaction"][0]["amount"]
            reward = block_data[1][0]["reward"]
            miner = block_data[1][0]["miner"]
            

            if sender == self.wallet.address:
                money_amount -= float(amount)

            if receiver == self.wallet.address:
                money_amount += float(amount)

            if miner == self.wallet.address:
                money_amount += float(reward)

        firebase_services.update_value(handyman.hash_email(self.email), "moneus_amount", money_amount) #update value on the database

        if float(money_amount) > float(self.wallet.money):
            notification = self.name,"adesso ha",money_amount,"moneus"
            self.write_on_logs(notification)

        self.wallet.money = money_amount
            

        return self.wallet.money

    def get_transactions(self):

        self.transactions.clear()
        
        with open('src.json') as blockchain_file:
            blockchain_data = json.load(blockchain_file)

        for block_data in blockchain_data.items():
            
            block_number = block_data[0]
            sender = block_data[1][0]["transaction"][0]["sender"]
            receiver = block_data[1][0]["transaction"][0]["receiver"]
            amount = block_data[1][0]["transaction"][0]["amount"]
            signature = block_data[1][0]["transaction"][0]["signature"]
            reward = block_data[1][0]["reward"]
            miner = block_data[1][0]["miner"]
            
            if sender == self.wallet.address:
                transaction = Transaction(sender, receiver, amount, signature)
                self.transactions.append(transaction)

            if receiver == self.wallet.address:
                transaction = Transaction(sender, receiver, amount, signature)
                self.transactions.append(transaction)

            if miner == self.wallet.address:
                transaction = Transaction("network", self.wallet.address, reward, block_number)
                self.transactions.append(transaction)

        return self.transactions

    def show_transactions(self):
        transactions = self.get_transactions()

        for i in transactions:
            if i.sender == self.wallet.address:
                print("you've sent",i.amount,"moneus to",i.receiver)
            elif i.receiver == self.wallet.address:
                print("you've received",i.amount,"moneus from",i.sender)    

    def write_on_logs(self,message):
        logs_file = open("logs.log", "r+")
        message = str(self.name) + " " + str(message) + "\n"
        if message not in logs_file:
            logs_file.write(message)
        logs_file.close()

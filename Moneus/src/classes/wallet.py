# pyright: reportMissingImports=false

#libraries

class Wallet:

    def __init__(self, address, money):
        self.address = address
        self.money = money
    
    def show(self):
        print("address:",self.address)
        print("money:",self.money)
from classes import Asset

class BuyHold:
    # Constructor
    def __init__(self, Asset:Asset):
        self.asset = Asset

    # Methods
    def performance(self, duration:int, end):
        print("t")
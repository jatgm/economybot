import sqlite3
import time
import json

class database():
    def __init__(self):
        self.con = sqlite3.connect('example.db')
        self.cur = self.con.cursor()
        # Create table
        self.cur.execute('''CREATE TABLE IF NOT EXISTS accounts (discordid integer, money real, bank real, networth real, lasttime real, occupation integer, banktier integer, username text)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS messagelog (discordid integer, username text, message text)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS items (discordid integer, attackcooldown real)''')
        self.con.commit()

        with open("data.json", "r") as f:
            self.data = json.load(f)

    def TransferMoney(self, sender, reciever, amount):
        self.cur.execute(f'UPDATE accounts set money = {self.CheckBalance(sender)-amount} WHERE discordid = "{sender}"')
        self.cur.execute(f'UPDATE accounts SET money = {self.CheckBalance(reciever)+amount} WHERE discordid = "{reciever}"')
        self.con.commit()

    def DoesUserExist(self, discordid):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                return True

    def CreateAccount(self, discordid, username):
        self.cur.execute("INSERT INTO accounts VALUES (?,?,?,?,?,?,?,?)", (int(discordid), float(55.0), float(0.0), float (0.0), float(time.time()), int(0), int(0), str(username)))
        self.cur.execute(f"INSERT INTO items (discordid, attackcooldown) VALUES ({int(discordid)}, {float(time.time())})")
        self.con.commit()

    def CheckCooldown(self, discordid):
        for row in self.cur.execute('SELECT * FROM items'):
            if row[0] == discordid:
                if time.time()-row[1] > 60:
                    self.cur.execute(f'UPDATE items SET attackcooldown = {time.time()} WHERE discordid = "{discordid}"')
                    return True
                else:
                    return '{:.2f}'.format(60-(time.time()-row[1]))

    def ReadyForPromotion(self, discordid):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                if row[5] < len(self.data["jobs"])-1:
                    if row[3] >= self.data["jobs"][row[5]+1]["requirement"]:
                        self.cur.execute(f'UPDATE accounts set occupation = {row[5]+1} WHERE discordid = "{discordid}"')
                        self.con.commit()
                        if row[5] >= len(self.data["jobs"])-2:
                            return True
                        if row[3] >= self.data["jobs"][row[5]+2]["requirement"]:
                            while True:
                                self.cur.execute(f'UPDATE accounts set occupation = {row[5]+1} WHERE discordid = "{discordid}"')
                                self.con.commit()
                                for row in self.cur.execute('SELECT * FROM accounts'):
                                    if row[0] == discordid:
                                        if row[5] >= len(self.data["jobs"])-1:
                                            return True
                                        if row[3] >= self.data["jobs"][row[5]+1]["requirement"]:
                                            break
                                        else:
                                            return True
                        return True
                        
    def CheckBalance(self, discordid):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                updatedBalance = row[1] + ((time.time()-row[4])/3600)*self.CheckWage(discordid)
                self.cur.execute(f'UPDATE accounts set lasttime = {time.time()} WHERE discordid = "{discordid}"')
                self.cur.execute(f'UPDATE accounts SET money = {updatedBalance} WHERE discordid = "{discordid}"')
                self.cur.execute(f'UPDATE accounts SET networth = {updatedBalance + self.CheckBank(discordid)} WHERE discordid = "{discordid}"')
                self.con.commit()
                return (row[1] + ((time.time()-row[4])/3600)*self.CheckWage(discordid))

    def EmojiDecoder(self, name):
        if name == ":tea:":
            return "🍵"
        if name == ":bank:":
            return "🏦"
        if name == ":skull:":
            return "💀"
        if name == ":shield:":
            return "🛡️"

    def CheckStoreAliasByName(self, name):
        for i in self.data["items"]:
            if i["name"] == name:
                return i["alias"]

    def CheckStoreDescriptionByName(self, name):
        for i in self.data["items"]:
            if i["name"] == name:
                return i["description"]

    def CheckStoreEmojiByName(self, name):
        for i in self.data["items"]:
            if i["name"] == name:
                return self.EmojiDecoder(i["emoji"])

    def GetIndexOfItem(self, name, discordid):
        for row in self.cur.execute(f'SELECT {name} FROM items WHERE discordid = "{discordid}"'):
            return row[0]

    def BuyItem(self, discordid, item, quantity, price):
        for row in self.cur.execute('SELECT * FROM items'):
            if row[0] == discordid:
                self.cur.execute(f'UPDATE accounts set money = {self.CheckBalance(discordid)-price} WHERE discordid = "{discordid}"')
                self.cur.execute(f'UPDATE items set {self.CheckStoreAliasByName(item)}Quantity = {int(self.GetIndexOfItem(f"{self.CheckStoreAliasByName(item)}Quantity", discordid))+quantity} WHERE discordid = "{discordid}"')
                self.con.commit()

    def CheckStoreDurationByName(self, name):
        for i in self.data["items"]:
            if i["name"] == name:
                return i["duration"]

    def EquipItem(self, item, discordid):
        for row in self.cur.execute(f'SELECT {self.CheckStoreAliasByName(item)}Cooldown FROM items WHERE discordid= "{discordid}"'):
            if row[0] == 0:
                self.cur.execute(f'UPDATE items set {self.CheckStoreAliasByName(item)}Cooldown = {time.time()} WHERE discordid = "{discordid}"')
                self.con.commit()
                return False
            else:
                if time.time() - row[0] <= self.CheckStoreDurationByName(item):
                    return self.CheckStoreDurationByName(item) - (time.time() - row[0])

    def CheckStoreNames(self):
        e = []
        for i in range(len(self.data["items"])):
            e.append(self.data["items"][i]["name"])
        return e

    def CheckInventoryNames(self, discordid):
        e = []
        for i in self.CheckStoreNames():
            if i != "Bank Tier Upgrade":
                for row in self.cur.execute(f'SELECT {self.CheckStoreAliasByName(i)}Quantity FROM items WHERE discordid = "{discordid}"'):
                    if row[0] != 0:
                        e.append(i)
        return e

    def CheckStorePrices(self, name):
        return (self.data["items"][name]["price"])
    
    def CheckStorePriceByName(self, name):
        for i in self.data["items"]:
            if i["name"] == name:
                return int(i["price"])

    def CheckStoreDescription(self, name):
        return (self.data["items"][name]["description"])


    def UpgradeBank(self, discordid):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                self.cur.execute(f'UPDATE accounts set banktier = {row[6]+1} WHERE discordid = "{discordid}"')
                self.con.commit()

    def CheckBank(self, discordid):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                return (row[2])

    def CheckBankLimit(self, discordid, next=False):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                if next:
                    return self.data["banks"][row[6]+1]["max"]
                else:
                    return self.data["banks"][row[6]]["max"]

    def CheckBankIndex(self, discordid):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                return row[6]

    def CheckBankTiersCurrently(self):
        return int(len(self.data["banks"]))

    def CheckBankTier(self, discordid, next=False):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                if next:
                    return self.data["banks"][row[6]+1]["abbreviated"]
                else:
                    return self.data["banks"][row[6]]["abbreviated"]

    def CheckBankPrice(self, discordid, next=False):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                if next:
                    return self.data["banks"][row[6]+1]["price"]
                else:
                    return self.data["banks"][row[6]]["price"]

    def CheckBankFees(self, discordid):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                return self.data["banks"][row[6]]["fees"]

    def CheckBankTierName(self, discordid, next=False):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                if next:
                    return self.data["banks"][row[6]+1]["name"]
                else:
                    return self.data["banks"][row[6]]["name"]

    def CheckOccupation(self, discordid):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                return self.data["jobs"][row[5]]["name"]

    def CheckWage(self, discordid):
        for row in self.cur.execute('SELECT * FROM accounts'):
            if row[0] == discordid:
                return self.data["jobs"][row[5]]["wage"]

    def AddItem(self, name):
        self.cur.execute(f"ALTER TABLE items ADD {name} INTEGER DEFAULT 0")
        self.con.commit()

    def RemoveItem(self, name):
        self.cur.execute(f"ALTER TABLE items DROP COLUMN {name}")
        self.con.commit()

    def DepositBank(self, discordid, amount):
        self.cur.execute(f'UPDATE accounts set money = {self.CheckBalance(discordid)-amount} WHERE discordid = "{discordid}"')
        self.cur.execute(f'UPDATE accounts set bank = {self.CheckBank(discordid)+amount} WHERE discordid = "{discordid}"')
        self.con.commit()

    def LogMessage(self, discordid, username, message):
        self.cur.execute("INSERT INTO messagelog VALUES (?,?,?)", (int(discordid), str(message), str(username)))
        self.con.commit()

    def ResetDatabase(self):
        self.cur.execute('''DROP TABLE accounts''')
        self.cur.execute('''DROP TABLE items''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS accounts (discordid integer, money real, bank real, networth real, lasttime real, occupation integer, banktier integer, username text)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS items (discordid integer, attackcooldown real)''')
        self.AddItem("shieldQuantity")
        self.AddItem("shieldCooldown")
        self.AddItem("teaQuantity")
        self.AddItem("teaCooldown")
        self.con.commit()

import MySQLdb
import asyncio
from nats.aio.client import Client as NATS
import time
import json
import sys

# SCRIPT POUR L'INSERTION DE DONNEES

def connect():
    try:
        connection = MySQLdb.connect(host=database_address, user="toto", password="toto", db="sae")
        return connection
    except:
        time.sleep(2)
    return connect()

def insert(account_id, amount):
    try:
        conn = connect()
        cursor = conn.cursor()
        print(f"NATS - DEPOSIT {amount} Euros INTO account {account_id}")
        cursor.execute(f"SELECT balance FROM account WHERE id ='{account_id}'")
        balance = float(cursor.fetchone()[0])
        cursor.execute(f"UPDATE account SET balance = '{str(float(balance) + float(amount))}' WHERE id = '{account_id}'")
        conn.commit()
        return True
    except Exception as error:
        print(error)
        return False

def create(account_name):
    try:
        conn = connect()
        cursor = conn.cursor()
        print(f"NATS - CREATE ACCOUNT name : {account_name}")
        cursor.execute(f"INSERT INTO account (name, balance) VALUES ('{account_name}', 0)")
        conn.commit()
        print("success")
        return True
    except Exception as error:
        print(error)
        return False

class Main:
    def __init__(self, address):
        self.nc = None
        self.server_address = address
        self.queue_group = "lb"
        self.topic_name = "sae/insert"

    async def run(self):
        self.nc = NATS()
        await self.nc.connect(servers=[self.server_address])
        await self.subscribe()
        while True:
            await asyncio.sleep(1)

    async def handle_message(self, msg):
        data = json.loads(msg.data.decode())
        action = data["action"]
        print(f"New message : {data}")
        # SIMULATE WORKLOAD
        time.sleep(60)
        if action == 1:  # Insertion d'argent
            account_id = data["account_id"]
            amount = data["amount"]
            insert(account_id, amount)
        elif action == 2:  # Creation de compte
            name = data["name"]
            create(name)

    async def subscribe(self):
        await self.nc.subscribe(self.topic_name, queue=self.queue_group, cb=self.handle_message)
        print(f"Subscribed to TOPIC : {self.topic_name}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    if len(sys.argv) == 1:
        server_address = "nats://192.168.56.105:4222"
        database_address = "192.168.56.105"
    else:
        server_address = sys.argv[1]
        database_address = sys.argv[2]
    main = Main(server_address)
    loop.run_until_complete(main.run())

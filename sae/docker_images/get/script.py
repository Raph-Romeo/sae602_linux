import MySQLdb
import asyncio
from nats.aio.client import Client as NATS
import json
import sys

# SCRIPT POUR LA CONSULTATION DE DONNEES

def connect():
    try:
        connection = MySQLdb.connect(host=database_address, user="toto", password="toto", db="sae")
        return connection
    except:
        time.sleep(2)
    return connect()

def get_account(account_id):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM account WHERE id ='{account_id}'")
        data = cursor.fetchone()
        return data
    except Exception as error:
        print(error)
        return False

def get_accounts():
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM account")
        data = cursor.fetchall()
        return data
    except Exception as error:
        print(error)
        return False

class Main:
    def __init__(self, address):
        self.nc = None
        self.server_address = address
        self.queue_group = "lb"
        self.topic_name = "sae/get"

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
        if action == 1:  # Get accounts
            reply_id = data["reply_id"]
            mysql_data = get_accounts()
            accounts = []
            for i in mysql_data:
                accounts.append({"id": i[0], "name": i[1], "balance": i[2]})
            reply_data = json.dumps({"accounts": accounts})
            await self.nc.publish(reply_id, reply_data.encode())
        elif action == 2:  # Get account details
            reply_id = data["reply_id"]
            account_id = data["account_id"]
            mysql_data = get_account(account_id)
            print(mysql_data)
            reply_data = json.dumps({"id": mysql_data[0], "name": mysql_data[1], "balance": mysql_data[2]})
            await self.nc.publish(reply_id, reply_data.encode())

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

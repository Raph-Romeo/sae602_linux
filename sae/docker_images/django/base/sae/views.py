from django.shortcuts import render
from django.http import HttpResponseRedirect
from .misc import Account
import json
import uuid

# NATS

from django.dispatch import Signal
import asyncio
import nats.aio.client as nats

nats_address = 'nats://172.16.1.30:4222'
nats_responses = {}

def publish_to_nats(sender, **kwargs):
    message = kwargs.get("message")
    subject = kwargs.get("subject")
    nc = nats.Client()

    async def run():
        await nc.connect(servers=[nats_address])
        await nc.publish(subject, message.encode())
        await nc.close()

    asyncio.run(run())

def publish_to_nats_and_response(sender, **kwargs):
    message = kwargs.get("message")
    subject = kwargs.get("subject")
    reply_id = kwargs.get("reply_id")
    nc = nats.Client()

    async def on_message(msg):
        nats_responses[reply_id] = json.loads(msg.data.decode())

    async def run():
        await nc.connect(servers=[nats_address])
        await nc.publish(subject, message.encode())
        subscription = await nc.subscribe(reply_id, cb=on_message, max_msgs=1)
        while subscription.delivered < 1:
            await asyncio.sleep(0.1)
    asyncio.run(run())

def index(request):
    nats_publish_signal = Signal()
    nats_publish_signal.connect(publish_to_nats_and_response)
    reply_id = str(uuid.uuid4())
    message = {"reply_id": reply_id, "action": 1}
    nats_publish_signal.send(sender=None, message=json.dumps(message), subject='sae/get', reply_id=reply_id)
    print(nats_responses[reply_id])
    accounts = []
    for account in nats_responses[reply_id]["accounts"]:
        accounts.append(Account(account["id"], account["name"], account["balance"]))
    return render(request, "index.html", {"accounts": accounts})


def index_redirect(request):
    return HttpResponseRedirect("/")


def account(request, id):
    if request.method == "POST":
        amount = request.POST.get("amount")
        nats_publish_signal = Signal()
        nats_publish_signal.connect(publish_to_nats)
        message = {"action": 1, "amount": amount, "account_id": id}
        nats_publish_signal.send(sender=None, message=json.dumps(message), subject='sae/insert')
        return render(request, "message.html", {"message": "Your deposit is currently being processed."})
    else:
        nats_publish_signal = Signal()
        nats_publish_signal.connect(publish_to_nats_and_response)
        reply_id = str(uuid.uuid4())
        message = {"reply_id": reply_id, "action": 2, "account_id": id}
        nats_publish_signal.send(sender=None, message=json.dumps(message), subject='sae/get', reply_id=reply_id)
        a = nats_responses[reply_id]
        print(a)
        return render(request, "account.html", {"account": Account(a["id"], a["name"], a["balance"])})


def create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        nats_publish_signal = Signal()
        nats_publish_signal.connect(publish_to_nats)
        message = {"action": 2, "name": name}
        nats_publish_signal.send(sender=None, message=json.dumps(message), subject='sae/insert')
        return render(request, "message.html", {"message": f"Account '{name}' is being created please wait."})
    else:
        return render(request, "create.html")

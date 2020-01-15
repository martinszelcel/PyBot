import discord
import settings
from models import *
from db import Session

client = discord.Client()
session = Session()

@client.event
async def on_ready():
    pass

@cleint.event
async def on_message(message):
    pass

@client.event
async def on_raw_message_delete(payload):
    pass

@client.event
async def on_raw_reaction_add(payload):
    pass

@client.event
async def on_raw_reaction_remove(payload):
    pass

@client.event
async def on_raw_reaction_clear(payload):
    pass

@client.event
async def on_member_join(member)

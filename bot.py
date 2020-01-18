import discord
from settings import ALLOWED_CHANNELS_ID, MESSAGE_EXP, EMOJIS, DISCORD_TOKEN
from models import User, Message
from utils import reset_users_exp, recalculate_all_exp

client = discord.Client()

@client.event
async def on_ready():
    print(f'Logged as {client.user}')

    print("Reseting all users experience. It will be calulated again in a moment...")
    reset_users_exp()

    print("Calculating EXP for all users using messages from channels history...")
    await recalculate_all_exp(client)

    print("Initialization done. Listening to new events...")


@client.event
async def on_message(message):
    if message.channel.id in ALLOWED_CHANNELS_ID:
        message_model = Message(id=message.id, user_id=message.author.id, is_bot=message.author.bot)
        if not message.author.bot:
            message_model.exp += MESSAGE_EXP
            user = User.get_or_create_and_add_exp(id=message.author.id, exp=message_model.exp, name=message.author.display_name)
            print(f"{user.name} has got {message_model.exp}EXP for writing message. {user.name} has now {user.exp}EXP!")


@client.event
async def on_raw_message_delete(payload):
    if payload.channel_id in ALLOWED_CHANNELS_ID:
        message = Message.pop(payload.message_id)
        if not message.is_bot:
            user = User.get_or_create_and_add_exp(id=message.user_id, exp=-message.exp)
            print(f"{user.name} has lost {message.exp}EXP because of his message being removed. {user.name} has now {user.exp}EXP.")

@client.event
async def on_raw_bulk_message_delete(payload):
    if payload.channel_id in ALLOWED_CHANNELS_ID:
        for message_id in payload.message_ids:
            message = Message.pop(message_id)
            if not message.is_bot:
                user = User.get_or_create_and_add_exp(id=message.user_id, exp=-message.exp)
                print(f"{user.name} has lost {message.exp}EXP because of his message being removed. {user.name} has now {user.exp}EXP.")

@client.event
async def on_raw_reaction_add(payload):
    if payload.channel_id in ALLOWED_CHANNELS_ID:
        emoji = payload.emoji.name
        valid_emoji = list(filter(lambda tup: emoji in tup, EMOJIS))
        message = Message.get(payload.message_id)
        if valid_emoji and not message.is_bot:
            emoji, exp = valid_emoji[0]
            user = User.get_or_create_and_add_exp(id=message.user_id, exp=exp)
            message.exp += exp
            print(f"{user.name} has got {exp}EXP for getting a reaction. {user.name} has now {user.exp}EXP!")


@client.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id in ALLOWED_CHANNELS_ID:
        emoji = payload.emoji.name
        valid_emoji = list(filter(lambda tup: emoji in tup, EMOJIS))
        message = Message.get(payload.message_id)
        if valid_emoji and not message.is_bot:
            emoji, exp = valid_emoji[0]
            user = User.get_or_create_and_add_exp(id=message.user_id, exp=-exp)
            message.exp -= exp
            print(f"{user.name} has lost {exp}EXP because of losing a reaction. {user.name} has now {user.exp}EXP!")


@client.event
async def on_raw_reaction_clear(payload):
    if payload.channel_id in ALLOWED_CHANNELS_ID:
        message = Message.get(payload.message_id)

        if not message.is_bot:
            exp = message.exp - MESSAGE_EXP
            user = User.get_or_create_and_add_exp(id=message.user_id, exp=-exp)
            message.exp = MESSAGE_EXP
            print(f"{user.name} has lost {exp}EXP because of all reactions cleared. {user.name} has not {user.exp}EXP!")

@client.event
async def on_member_join(member):
    member.send(content="Welcome!")

@client.event
async def on_member_update(before, after):
    if before.display_name != after.display_name:
        print(f"{before.name} changed his nickname to {after.display_name}")
        User.update(name=after.display_name).where(User.id == after.id).execute()

client.run(DISCORD_TOKEN)

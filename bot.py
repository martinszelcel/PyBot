import discord
from settings import ALLOWED_CHANNELS_ID, MESSAGE_EXP, EMOJIS, DISCORD_TOKEN
from models import User, Message

client = discord.Client()
messages_by_id = {}

@client.event
async def on_ready():
    print(f'Logged as {client.user}')

    print("Reseting all users experience. It will be calulated again in a moment...")
    User.update(exp=0).execute()


    print("Calculating EXP for all users using messages from channels history...")
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.type == discord.ChannelType.text and channel.id in ALLOWED_CHANNELS_ID:
                async for message in channel.history():
                    message_model = Message(id=message.id, exp=0, user_id=message.author.id, is_bot=message.author.bot)
                    messages_by_id[message.id] = message_model

                    if not message.author.bot:
                        message_model.exp += MESSAGE_EXP

                        for reaction in message.reactions:
                            emoji = reaction.emoji if type(reaction.emoji) is str else reaction.emoji.name

                            valid_emoji = list(filter(lambda tup: emoji in tup, EMOJIS))
                            if valid_emoji:
                                emoji, exp = valid_emoji[0]
                                message_model.exp += exp

                        user, created = User.get_or_create(id=message.author.id)
                        user.name = message.author.display_name
                        user.add_exp(message_model.exp)
                        user.save()

    print("Initialization done. Listening to new events...")


@client.event
async def on_message(message):
    message_model = Message(id=message.id, exp=0, user_id=message.author.id, is_bot=message.author.bot)
    messages_by_id[message.id] = message_model
    if not message.author.bot:
        message_model.exp += MESSAGE_EXP
        user = User.get(id=message.author.id)
        user.add_exp(message_model.exp)
        user.save()
        print(f"{user.name} has got {message_model.exp}EXP for writing message. {user.name} has now {user.exp}EXP!")


@client.event
async def on_raw_message_delete(payload):
    message = messages_by_id.pop(payload.message_id)

    if not message.is_bot:
        user = User.get(id=message.user_id)
        user.remove_exp(message.exp)
        user.save()
        print(f"{user.name} has lost {message.exp}EXP because of his message being removed. {user.name} has now {user.exp}EXP.")

@client.event
async def on_raw_bulk_message_delete(payload):
    for message_id in payload.message_ids:
        message = messages_by_id.pop(message_id)

        if not message.is_bot:
            user = User.get(id=message.user_id)
            user.remove_exp(message.exp)
            user.save()
            print(f"{user.name} has lost {message.exp}EXP because of his message being removed. {user.name} has now {user.exp}EXP.")

@client.event
async def on_raw_reaction_add(payload):
    emoji = payload.emoji.name

    valid_emoji = list(filter(lambda tup: emoji in tup, EMOJIS))
    message = messages_by_id[payload.message_id]
    if valid_emoji and not message.is_bot:
        emoji, exp = valid_emoji[0]
        user = User.get(id=message.user_id)
        user.add_exp(exp)
        user.save()
        message.exp += exp
        print(f"{user.name} has got {exp}EXP for getting a reaction. {user.name} has now {user.exp}EXP!")


@client.event
async def on_raw_reaction_remove(payload):
    emoji = payload.emoji.name

    valid_emoji = list(filter(lambda tup: emoji in tup, EMOJIS))
    message = messages_by_id[payload.message_id]
    if valid_emoji and not message.is_bot:
        emoji, exp = valid_emoji[0]
        user = User.get(id=message.user_id)
        user.remove_exp(exp)
        user.save()
        message.exp -= exp
        print(f"{user.name} has lost {exp}EXP because of losing a reaction. {user.name} has now {user.exp}EXP!")


@client.event
async def on_raw_reaction_clear(payload):
    message = messages_by_id[payload.message_id]

    if not message.is_bot:
        user = User.get(id=message.user_id)
        exp = message.exp - MESSAGE_EXP
        if exp > 0:
            user.remove_exp(exp)
        else:
            user.add_exp(-exp)
        user.save()
        message.exp = MESSAGE_EXP
        print(f"{user.name} has lost {exp}EXP because of all reactions cleared. {user.name} has not {user.exp}EXP!")

@client.event
async def on_member_join(member):
    member.dm_channel.send(content="Welcome!")

@client.event
async def on_member_update(before, after):
    if before.display_name != after.display_name:
        print(f"{before.name} changed his nickname to {after.display_name}")
        User.update(name=after.display_name).where(User.id == after.id).execute()

client.run(DISCORD_TOKEN)

import discord
from models import User, Message
from settings import ALLOWED_CHANNELS_ID, MESSAGE_EXP, EMOJIS

def reset_users_exp():
    User.update(exp=0).execute()


async def recalculate_all_exp(client):
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.type == discord.ChannelType.text and channel.id in ALLOWED_CHANNELS_ID:
                async for message in channel.history():
                    message_model = Message(id=message.id, user_id=message.author.id, is_bot=message.author.bot)

                    if not message.author.bot:
                        message_model.exp += MESSAGE_EXP

                        for reaction in message.reactions:
                            emoji = reaction.emoji if type(reaction.emoji) is str else reaction.emoji.name

                            valid_emoji = list(filter(lambda tup: emoji in tup, EMOJIS))
                            if valid_emoji:
                                emoji, exp = valid_emoji[0]
                                message_model.exp += exp

                        User.get_or_create_and_add_exp(id=message.author.id, exp=message_model.exp, name=message.author.display_name)

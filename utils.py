import discord
from models import User, Message
from settings import ALLOWED_CHANNELS_ID, MESSAGE_EXP, EMOJIS

def reset_users_exp():
    User.update(exp=0).execute()

def get_number_emoji(number):
    emojis = [':zero:',':one:', ':two:', ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":keycap_ten:"]
    if number > 10:
        number = str(number)
        result = ""
        for digit in number:
            result += emojis[int(digit)]
    else:
        result = emojis[number]
    return result

async def calculate_all_exp(bot):
    for guild in bot.guilds:
        for channel in guild.channels:
            if channel.type == discord.ChannelType.text and channel.id in ALLOWED_CHANNELS_ID:
                async for message in channel.history(limit=None):
                    message_model = Message(id=message.id, user_id=message.author.id, is_bot=message.author.bot, is_command=Message.is_command(message, bot))
                    if not message.author.bot and not message_model.is_command:
                        message_model.exp += MESSAGE_EXP

                        for reaction in message.reactions:
                            emoji = reaction.emoji if type(reaction.emoji) is str else reaction.emoji.name

                            valid_emoji = list(filter(lambda tup: emoji in tup, EMOJIS))
                            if valid_emoji:
                                emoji, exp = valid_emoji[0]
                                message_model.exp += exp

                        await User.get_or_create_and_add_exp(id=message.author.id, exp=message_model.exp, name=message.author.display_name)

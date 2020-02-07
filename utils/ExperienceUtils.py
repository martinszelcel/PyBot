import discord
from models.ExperienceModels import User, Message
from main import settings as main_settings
from tinydb import where

NAME = "Experience"

settings = main_settings.table(NAME)

def reset_users_exp():
    User.update(exp=0).execute()

async def calculate_all_exp(bot):
    for guild in bot.guilds:
        for channel in guild.channels:
            exp_channels = settings.get(where('key') == 'exp_channels')['value']
            if channel.type == discord.ChannelType.text and (channel.id in exp_channels or '*' in exp_channels):
                async for message in channel.history(limit=None):
                    message_model = Message(id=message.id, user_id=message.author.id, is_bot=message.author.bot, is_command=Message.is_command(message, bot))
                    if not message.author.bot and not message_model.is_command:
                        message_model.exp += settings.get(where('key') == 'message_exp')['value']

                        exp_emojis = settings.get(where('key') == 'exp_emojis')['value']
                        for reaction in message.reactions:
                            emoji = reaction.emoji if type(reaction.emoji) is str else reaction.emoji.name

                            valid_emoji = list(filter(lambda elem: emoji in elem["name"], exp_emojis))
                            if valid_emoji:
                                exp = valid_emoji[0]["exp"]
                                message_model.exp += exp

                        await User.get_or_create_and_add_exp(id=message.author.id, exp=message_model.exp, name=message.author.display_name)

import discord
from discord.ext import commands
from utils import reset_users_exp, calculate_all_exp
from models import User, Message
from settings import ALLOWED_CHANNELS_ID, MESSAGE_EXP, EMOJIS
from lang import experience as lang
import importlib

class ExperienceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_ready')
    async def ready(self):
        print(lang.EXP_RESET)
        reset_users_exp()

        print(lang.EXP_CALCULATION)
        await calculate_all_exp(self.bot)

        print(lang.INITIALIZATION_DONE)

    @commands.command(name='level', aliases=['lvl', 'exp'])
    async def level(self, ctx, *, member: discord.Member=None):
        if not member:
            member = ctx.author

        if member.bot:
            await ctx.send(lang.LEVEL_BOT_RESPONSE.format(message_author=ctx.author.display_name))
            return

        print(member.name)
        user, created = User.get_or_create(id=member.id)
        await ctx.send(lang.LEVEL_COMMAND_RESPONSE.format(user_name=user.name, user_exp=user.exp, user_level=user.level, message_author=ctx.author.display_name))

    async def cog_command_error(self, ctx, error):
        await ctx.send(error)

    @commands.Cog.listener('on_message')
    async def new_message(self, message):
        if message.channel.id in ALLOWED_CHANNELS_ID:
            message_model = Message(id=message.id, user_id=message.author.id, is_bot=message.author.bot)
            if not message.author.bot:
                message_model.exp += MESSAGE_EXP
                user = User.get_or_create_and_add_exp(id=message.author.id, exp=message_model.exp, name=message.author.display_name)
                print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=message_model.exp, reason=lang.FOR_WRITING_MESSAGE_REASON))

    @commands.Cog.listener('on_raw_message_delete')
    async def message_removed(self, payload):
        if payload.channel_id in ALLOWED_CHANNELS_ID:
            message = Message.pop(payload.message_id)
            if not message.is_bot:
                user = User.get_or_create_and_add_exp(id=message.user_id, exp=-message.exp)
                if message.exp > 0:
                    print(lang.USER_LOST_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_lost=message.exp, reason=lang.FOR_MESSAGE_REMOVED_REASON))
                else:
                    print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=message.exp, reason=lang.FOR_MESSAGE_REMOVED_REASON))

    @commands.Cog.listener('on_raw_bulk_message_delete')
    async def bulk_message_removed(self, payload):
        if payload.channel_id in ALLOWED_CHANNELS_ID:
            for message_id in payload.message_ids:
                message = Message.pop(message_id)
                if not message.is_bot:
                    user = User.get_or_create_and_add_exp(id=message.user_id, exp=-message.exp)
                    if message.exp > 0:
                        print(lang.USER_LOST_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_lost=message.exp, reason=lang.FOR_MESSAGE_REMOVED_REASON))
                    else:
                        print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=message.exp, reason=lang.FOR_MESSAGE_REMOVED_REASON))

    @commands.Cog.listener('on_raw_reaction_add')
    async def new_reaction(self, payload):
        if payload.channel_id in ALLOWED_CHANNELS_ID:
            emoji = payload.emoji.name
            valid_emoji = list(filter(lambda tup: emoji in tup, EMOJIS))
            message = Message.get(payload.message_id)
            if valid_emoji and not message.is_bot:
                emoji, exp = valid_emoji[0]
                user = User.get_or_create_and_add_exp(id=message.user_id, exp=exp)
                message.exp += exp
                if exp > 0:
                    print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=exp, reason=lang.FOR_GETTING_A_REACTION))
                else:
                    print(lang.USER_LOST_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_lost=exp, reason=lang.FOR_GETTING_A_REACTION))

    @commands.Cog.listener('on_raw_reaction_remove')
    async def reaction_removed(self, payload):
        if payload.channel_id in ALLOWED_CHANNELS_ID:
            emoji = payload.emoji.name
            valid_emoji = list(filter(lambda tup: emoji in tup, EMOJIS))
            message = Message.get(payload.message_id)
            if valid_emoji and not message.is_bot:
                emoji, exp = valid_emoji[0]
                user = User.get_or_create_and_add_exp(id=message.user_id, exp=-exp)
                message.exp -= exp
                if exp > 0:
                    print(lang.USER_LOST_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_lost=exp, reason=lang.FOR_LOSING_A_REACTION))
                else:
                    print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=exp, reason=lang.FOR_LOSING_A_REACTION))

    @commands.Cog.listener('on_raw_reaction_clear')
    async def reactions_cleared(self, payload):
        if payload.channel_id in ALLOWED_CHANNELS_ID:
            message = Message.get(payload.message_id)

            if not message.is_bot:
                exp = message.exp - MESSAGE_EXP
                user = User.get_or_create_and_add_exp(id=message.user_id, exp=-exp)
                message.exp = MESSAGE_EXP
                if exp > 0:
                    print(lang.USER_LOST_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_lost=exp, reason=lang.FOR_REACTIONS_REMOVED))
                else:
                    print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=exp, reason=lang.FOR_REACTIONS_REMOVED))

def setup(bot):
    importlib.reload(lang)
    bot.add_cog(ExperienceCog(bot))

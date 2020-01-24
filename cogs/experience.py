import discord
from discord.ext import commands
from utils import reset_users_exp, calculate_all_exp, get_number_emoji
from models import User, Message
from settings import ALLOWED_CHANNELS_ID, MESSAGE_EXP, EMOJIS, ADMIN_ROLE
from lang import experience as lang
import importlib

class ExperienceCog(commands.Cog, name="Levels and EXP"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_ready')
    async def ready(self):
        print(lang.EXP_RESET)
        reset_users_exp()

        print(lang.EXP_CALCULATION)
        await calculate_all_exp(self.bot)

        print(lang.INITIALIZATION_DONE)

    @commands.command(name='level', aliases=['lvl', 'exp', 'stats'])
    async def level(self, ctx, *, member: discord.Member=None):
        if not member:
            member = ctx.author

        if member.bot:
            embed = discord.Embed(title=lang.LEVEL_BOT_RESPONSE.format(message_author=ctx.author.display_name))
        else:
            user, created = User.get_or_create(id=member.id)
            embed = discord.Embed(title=lang.LEVEL_COMMAND_RESPONSE.format(user_name=user.name, user_exp=user.exp, user_level=user.level, message_author=ctx.author.display_name, user_next_level_exp=User.get_level_exp(user.level + 1)))
        await ctx.send(embed=embed)

    @commands.command(name='rank', aliases=['top'])
    async def rank(self, ctx):
        embed = discord.Embed(title=":trophy: Top users:", color=0xfed142)
        for index, user in enumerate(User.select().order_by(-User.exp).limit(10)):
            embed.add_field(name="Level {level}    {exp}EXP/{next_level_exp}EXP".format(level=user.level, exp=user.exp, next_level_exp=User.get_level_exp(user.level + 1)), value="{number} {name}".format(number=get_number_emoji(index + 1), name=user.name, level=user.level, exp=user.exp), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='recalculate')
    @commands.has_role(ADMIN_ROLE)
    async def recalculate_exp(self, ctx):
        print(lang.EXP_RESET)
        reset_users_exp()
        print(lang.EXP_CALCULATION)
        await calculate_all_exp(self.bot)
        embed = discord.Embed(title="All EXP has been recalculated.")
        await ctx.send(embed=embed)

    @commands.Cog.listener('on_message')
    async def new_message(self, message):
        if message.channel.id in ALLOWED_CHANNELS_ID:
            message_model = Message(id=message.id, user_id=message.author.id, is_bot=message.author.bot, is_command=Message.is_command(message, self.bot))
            if not message.author.bot and not message_model.is_command:
                message_model.exp += MESSAGE_EXP
                user = await User.get_or_create_and_add_exp(id=message.author.id, exp=message_model.exp, name=message.author.display_name, messageable=message.channel)
                print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=message_model.exp, reason=lang.FOR_WRITING_MESSAGE_REASON))

    @commands.Cog.listener('on_raw_message_delete')
    async def message_removed(self, payload):
        if payload.channel_id in ALLOWED_CHANNELS_ID:
            message = Message.pop(payload.message_id)
            if not message.is_bot and not message.is_command:
                user = await User.get_or_create_and_add_exp(id=message.user_id, exp=-message.exp, messageable=message.channel)
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
                    user = await User.get_or_create_and_add_exp(id=message.user_id, exp=-message.exp, messageable=message.channel)
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
            if valid_emoji and not message.is_bot and not message.is_command:
                emoji, exp = valid_emoji[0]
                user = await User.get_or_create_and_add_exp(id=message.user_id, exp=exp, messageable=message.channel)
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
            if valid_emoji and not message.is_bot and not message.is_command:
                emoji, exp = valid_emoji[0]
                user = await User.get_or_create_and_add_exp(id=message.user_id, exp=-exp, messageable=message.channel)
                message.exp -= exp
                if exp > 0:
                    print(lang.USER_LOST_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_lost=exp, reason=lang.FOR_LOSING_A_REACTION))
                else:
                    print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=exp, reason=lang.FOR_LOSING_A_REACTION))

    @commands.Cog.listener('on_raw_reaction_clear')
    async def reactions_cleared(self, payload):
        if payload.channel_id in ALLOWED_CHANNELS_ID:
            message = Message.get(payload.message_id)

            if not message.is_bot and not message.is_command:
                exp = message.exp - MESSAGE_EXP
                user = await User.get_or_create_and_add_exp(id=message.user_id, exp=-exp, messageable=message.channel)
                message.exp = MESSAGE_EXP
                if exp > 0:
                    print(lang.USER_LOST_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_lost=exp, reason=lang.FOR_REACTIONS_REMOVED))
                else:
                    print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=exp, reason=lang.FOR_REACTIONS_REMOVED))

def setup(bot):
    importlib.reload(lang)
    bot.add_cog(ExperienceCog(bot))

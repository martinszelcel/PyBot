import discord
from discord.ext import commands
from utils import reset_users_exp, calculate_all_exp, get_number_emoji
from models import User, Message
from settings import ALLOWED_CHANNELS_ID, MESSAGE_EXP, EMOJIS, ADMIN_ROLE
import importlib
from lang import experience as lang


class ExperienceCog(commands.Cog, name="Experience"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_ready')
    async def ready(self):
        # Reset all users exp
        print(lang.EXP_RESET)
        reset_users_exp()

        # Calculate exp for all users
        print(lang.EXP_CALCULATION)
        await calculate_all_exp(self.bot)

        print(lang.INITIALIZATION_DONE)

    @commands.command(name='level', aliases=['lvl', 'exp', 'stats'])
    async def level(self, ctx, *, member: discord.Member=None):
        # If no member is specifed, check exp for message author
        if not member:
            member = ctx.author

        # Bots don't have levels and exp
        if member.bot:
            embed = discord.Embed(title=f":x: Sorry {ctx.author.display_name}! Levels are only for normal users.", color=0xc95351)
        else:
            # Get user and display embed with his level and exp
            user, created = User.get_or_create(id=member.id)
            embed = discord.Embed(title=f"**{user.name}**", color=0xfed142)
            embed.add_field(name="Level", value=f"**Level {user.level}**", inline=False)
            embed.add_field(name="Experience", value=f"**{user.exp}EXP/{User.get_level_exp(user.level + 1)}EXP**", inline=False)
        # Send generated embed
        await ctx.send(embed=embed)

    @commands.command(name='rank', aliases=['top'])
    async def rank(self, ctx):
        # Create embed
        embed = discord.Embed(title=":trophy: Top users:", color=0xfed142)

        # Add fields for 10 best users
        for index, user in enumerate(User.select().order_by(-User.exp).limit(10)):
            embed.add_field(name="Level {level}    {exp}EXP/{next_level_exp}EXP".format(level=user.level, exp=user.exp, next_level_exp=User.get_level_exp(user.level + 1)), value="**{number} {name}**".format(number=get_number_emoji(index + 1, medals=True), name=user.name, level=user.level, exp=user.exp), inline=False)
        # Send generated embed
        await ctx.send(embed=embed)

    @commands.command(name='reactions', aliases=['emojis'])
    async def reactions(self, ctx):
        # Create embed
        embed = discord.Embed(title="<:python_logo:666314420254933013> Reactions that give/take EXP:", color=0xfed142)

        # List all emojis and their EXP
        for emoji, exp in EMOJIS:
            embed.add_field(name="‏‏‎ ‎", value=f"{emoji} {exp}EXP", inline=False)
        # Send generated embed
        await ctx.send(embed=embed)

    @commands.command(name='recalculate')
    @commands.has_role(ADMIN_ROLE)
    async def recalculate_exp(self, ctx):
        # Reset all users exp
        print(lang.EXP_RESET)
        reset_users_exp()

        # Calculate exp for all users
        print(lang.EXP_CALCULATION)
        await calculate_all_exp(self.bot)

        # Generate embed and send it
        embed = discord.Embed(title=":white_check_mark: All EXP has been recalculated.", color=0x0cc974)
        await ctx.send(embed=embed)

    @commands.Cog.listener('on_message')
    async def new_message(self, message):
        # Check if the message channel is in the list
        if message.channel.id in ALLOWED_CHANNELS_ID:
            # Create new message model
            message_model = Message(id=message.id, user_id=message.author.id, is_bot=message.author.bot, is_command=Message.is_command(message, self.bot))
            # Check if message is no command, and the author is not a bot
            if not message.author.bot and not message_model.is_command:
                # Add exp to message and user
                message_model.exp += MESSAGE_EXP
                user = await User.get_or_create_and_add_exp(id=message.author.id, exp=message_model.exp, name=message.author.display_name)
                print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=message_model.exp, reason=lang.FOR_WRITING_MESSAGE_REASON))

    @commands.Cog.listener('on_raw_message_delete')
    async def message_removed(self, payload):
        # Check if the message channel is in the list
        if payload.channel_id in ALLOWED_CHANNELS_ID:
            # Pop message from cache
            message = Message.pop(payload.message_id)
            # Check if message is no command, and the author is not a bot
            if not message.is_bot and not message.is_command:
                # Update message author exp
                user = await User.get_or_create_and_add_exp(id=message.user_id, exp=-message.exp)
                if message.exp > 0:
                    print(lang.USER_LOST_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_lost=message.exp, reason=lang.FOR_MESSAGE_REMOVED_REASON))
                else:
                    print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=message.exp, reason=lang.FOR_MESSAGE_REMOVED_REASON))

    @commands.Cog.listener('on_raw_bulk_message_delete')
    async def bulk_message_removed(self, payload):
        # Check if the message channel is in the list
        if payload.channel_id in ALLOWED_CHANNELS_ID:
            for message_id in payload.message_ids:
                # Pop message from cache
                message = Message.pop(message_id)
                # Check if the message author is not a bot
                if not message.is_bot:
                    # Update message author exp
                    user = await User.get_or_create_and_add_exp(id=message.user_id, exp=-message.exp)
                    if message.exp > 0:
                        print(lang.USER_LOST_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_lost=message.exp, reason=lang.FOR_MESSAGE_REMOVED_REASON))
                    else:
                        print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=message.exp, reason=lang.FOR_MESSAGE_REMOVED_REASON))

    @commands.Cog.listener('on_raw_reaction_add')
    async def new_reaction(self, payload):
        # Check if the message channel is in the list
        if payload.channel_id in ALLOWED_CHANNELS_ID:
            emoji = payload.emoji.name
            # Check if emoji is in list
            valid_emoji = list(filter(lambda tup: emoji in tup, EMOJIS))
            # Get message from cache
            message = Message.get(payload.message_id)
            # Check if message is no command, the author is not a bot, and it is not message author reaction
            if valid_emoji and not message.is_bot and not message.is_command and message.user_id != payload.user_id:
                # Update message and author exp
                emoji, exp = valid_emoji[0]
                user = await User.get_or_create_and_add_exp(id=message.user_id, exp=exp)
                message.exp += exp
                if exp > 0:
                    print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=exp, reason=lang.FOR_GETTING_A_REACTION))
                else:
                    print(lang.USER_LOST_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_lost=exp, reason=lang.FOR_GETTING_A_REACTION))

    @commands.Cog.listener('on_raw_reaction_remove')
    async def reaction_removed(self, payload):
        # Check if the message channel is in the list
        if payload.channel_id in ALLOWED_CHANNELS_ID:
            emoji = payload.emoji.name
            # Check if emoji is in list
            valid_emoji = list(filter(lambda tup: emoji in tup, EMOJIS))
            # Get message from cache
            message = Message.get(payload.message_id)
            # Check if message is no command, the author is not a bot, and it is not message author reaction
            if valid_emoji and not message.is_bot and not message.is_command and message.user_id != payload.user_id:
                # Update message and author exp
                emoji, exp = valid_emoji[0]
                user = await User.get_or_create_and_add_exp(id=message.user_id, exp=-exp)
                message.exp -= exp
                if exp > 0:
                    print(lang.USER_LOST_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_lost=exp, reason=lang.FOR_LOSING_A_REACTION))
                else:
                    print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=exp, reason=lang.FOR_LOSING_A_REACTION))

    @commands.Cog.listener('on_raw_reaction_clear')
    async def reactions_cleared(self, payload):
        # Check if the message channel is in the list
        if payload.channel_id in ALLOWED_CHANNELS_ID:
            # Get message from cache
            message = Message.get(payload.message_id)
            # Check if message is no command, and the author is not a bot
            if not message.is_bot and not message.is_command:
                # Update message and author exp
                exp = message.exp - MESSAGE_EXP
                user = await User.get_or_create_and_add_exp(id=message.user_id, exp=-exp)
                message.exp = MESSAGE_EXP
                if exp > 0:
                    print(lang.USER_LOST_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_lost=exp, reason=lang.FOR_REACTIONS_REMOVED))
                else:
                    print(lang.USER_GOT_EXP.format(user_name=user.name, user_exp=user.exp, user_level=user.level, exp_got=exp, reason=lang.FOR_REACTIONS_REMOVED))

def setup(bot):
    importlib.reload(lang)
    bot.add_cog(ExperienceCog(bot))

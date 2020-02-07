import discord
from peewee import Model, IntegerField, CharField, SqliteDatabase
from settings import LEVEL_EXPONENT, LEVEL_BASE_EXP
from main import db, settings as main_settings
from tinydb import where
import math

NAME = "Experience"

settings = main_settings.table(NAME)

class User(Model):
    id = IntegerField(primary_key=True)
    name = CharField(null=True)
    level = IntegerField(default=0)
    exp = IntegerField(default=0)

    class Meta:
        database = db
        table_name = "users"

    @staticmethod
    def get_level_exp(level):
        return math.floor(settings.get(where('key') == 'base_level_exp')['value'] * (level ** settings.get(where('key') == 'level_exponent')['value']))

    async def add_exp(self, exp, messageable = None):
        # Add exp to self
        self.exp += exp

        # Calculate next level exp
        next_level_exp = User.get_level_exp(self.level + 1)

        while self.exp >= next_level_exp:
            # If user has enough exp change his level to higher
            if self.exp >= next_level_exp:
                await self.level_up(messageable)

            # Calculate again user next level exp
            next_level_exp = User.get_level_exp(self.level + 1)

    async def remove_exp(self, exp, messageable = None):
        # Remove exp from self
        self.exp -= exp

        # Calculate user level exp
        level_now_exp = User.get_level_exp(self.level)

        while self.exp < level_now_exp:
            # If user has too low exp for this level change his level to lower
            if self.exp < level_now_exp:
                await self.level_down(messageable)

            # Calculate again user level exp
            level_now_exp = User.get_level_exp(self.level)

    async def level_up(self, messageable = None):
        self.level += 1
        if messageable:
            embed = discord.Embed(title=f"Congratulations {self.name}! Your level now is {self.level}!")
            await messageable.send(embed=embed)

    async def level_down(self, messageable = None):
        self.level -= 1
        if messageable:
            embed = discord.Embed(title=f"Sorry {self.name}... Your level now is {self.level}")
            await messageable.send(embed=embed)

    @staticmethod
    async def get_or_create_and_add_exp(id, exp, name=None, messageable=None):
        ''' First the user is got from db or created if it doesn't exist. Next amount of exp is added or removed from this user.
        If name is supplied, the user name will be changed to it.
        Returns User instance.
        '''
        # Get or create a User
        user, created = User.get_or_create(id=id)
        # Add or remove exp if exp is negative number
        if exp > 0:
            await user.add_exp(exp, messageable)
        else:
            await user.remove_exp(abs(exp), messageable)

        # If name is supplied change it
        if name is not None:
            user.name = name
        # Save the user
        user.save()
        return user

class Message:
    messages = {}

    def __init__(self, id, user_id, is_bot=False, is_command=False, exp=0):
        self.id = id
        self.exp = exp
        self.user_id = user_id
        self.is_bot = is_bot
        self.is_command = is_command
        Message.messages[id] = self

    @staticmethod
    def get(id):
        return Message.messages[id]

    @staticmethod
    def pop(id):
        return Message.messages.pop(id)

    @staticmethod
    def is_command(message, bot):
        return True if len(message.content) > len(bot.command_prefix) and message.content[:len(bot.command_prefix)] == bot.command_prefix else False

db.create_tables([User])

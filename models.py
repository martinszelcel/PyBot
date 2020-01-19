from peewee import *
from settings import DATABASE, LEVELS

db = SqliteDatabase(DATABASE)

class User(Model):
    id = IntegerField(primary_key=True)
    name = CharField(null=True)
    level = IntegerField(default=0)
    exp = IntegerField(default=0)

    class Meta:
        database = db
        table_name = "users"

    def add_exp(self, exp):
        # Get all higher levels from settings
        higher_levels = list(filter(lambda tup: tup[0] > self.level, LEVELS))
        # Add exp to self
        self.exp += exp

        if len(higher_levels) > 0:
            # Assing to variables next higher level
            level, exp_needed = higher_levels[0]
            # If user has enough exp change his level to higher
            if self.exp >= exp_needed:
                self.change_level(level)

    def remove_exp(self,exp):
        # Get user level from settings (as a list)
        level_now = list(filter(lambda tup: tup[0] == self.level, LEVELS))
        # Remove exp from self
        self.exp -= exp

        if len(level_now) > 0:
            # Assing to variables next lower level
            level, exp_needed = level_now[0]
            # If user has too low exp for this level change his level to lower
            if self.exp < exp_needed:
                self.change_level(level - 1)

    def change_level(self, level):
        # Change level
        self.level = level

        # Print message
        if level > self.level:
            print(f"Congratulations {self.name}! Your level now is {level}!")
        elif level < self.level:
            print(f"Sorry {self.name}... Your level now is {level}")


    @staticmethod
    def get_or_create_and_add_exp(id, exp, name=None):
        ''' First the user is got from db or created if it doesn't exist. Next amount of exp is added or removed from this user.
        If name is supplied, the user name will be changed to it.
        Returns User instance.
        '''
        # Get or create a User
        user, created = User.get_or_create(id=id)
        # Add or remove exp if exp is negative number
        if exp > 0:
            user.add_exp(exp)
        else:
            user.remove_exp(abs(exp))

        # If name is supplied change it
        if name is not None:
            user.name = name
        # Save the user
        user.save()
        return user

class Message():
    messages = {}

    def __init__(self, id, user_id, is_bot, exp=0):
        self.id = id
        self.exp = exp
        self.user_id = user_id
        self.is_bot = is_bot
        Message.messages[id] = self

    @staticmethod
    def get(id):
        return Message.messages[id]

    @staticmethod
    def pop(id):
        return Message.messages.pop(id)

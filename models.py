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
        higher_levels = list(filter(lambda tup: tup[1] > self.exp, LEVELS))
        self.exp += exp
        if len(higher_levels) > 0:
            level, exp_needed = higher_levels[0]
            if self.exp >= exp_needed and self.level < level:
                self.change_level(level)

    def remove_exp(self,exp):
        lower_levels = list(filter(lambda tup: tup[1] <= self.exp, LEVELS))
        self.exp -= exp
        if len(lower_levels) > 0:
            lower_levels.reverse()
            level, exp_needed = lower_levels[0]
            if self.exp < exp_needed and self.level > level - 1:
                self.change_level(level - 1)

    def change_level(self, level):
        if level > self.level:
            print(f"Congratulations {self.name}! Your level now is {level}!")
        elif level < self.level:
            print(f"Sorry {self.name}... Your level now is {level}")
        self.level = level

    @staticmethod
    def get_or_create_and_add_exp(id, exp, name=None):
        user, created = User.get_or_create(id=id)
        if exp > 0:
            user.add_exp(exp)
        else:
            user.remove_exp(abs(exp))
        if name is not None:
            user.name = name
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

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
        level, exp_needed = list(filter(lambda tup: tup[1] > self.exp, LEVELS))[0]

        self.exp += exp
        if self.exp >= exp_needed and self.level < level:
            self.change_level(level)

    def remove_exp(self,exp):
        lower_levels = list(filter(lambda tup: tup[1] <= self.exp, LEVELS))
        lower_levels.reverse()
        level, exp_needed = lower_levels[0]

        self.exp -= exp
        if self.exp < exp_needed and self.level > level - 1:
            self.change_level(level - 1)

    def change_level(self, level):
        if level > self.level:
            print(f"Congratulations {self.name}! Your level now is {level}!")
        elif level < self.level:
            print(f"Sorry {self.name}... Your level now is {level}")
        self.level = level

class Message:
    messages = {}

    def __init__(self, id, exp, user_id, is_bot):
        self.id = id
        self.exp = exp
        self.user_id = user_id
        self.is_bot = is_bot

    

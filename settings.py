DATABASE = 'discord.db'
DISCORD_TOKEN = 'NjY2MzA3MDc2NDI2OTU2ODAx.XhyRhA.GJEUs9DW1H-tOIwUs1A_BMnmvgQ'

# Channels on with users will gain EXP
ALLOWED_CHANNELS_ID=[666298091657363469, ]

# EXP for single message
MESSAGE_EXP=10

# Reaction emojis that gives message authors EXP
# Syntax: (<emoji>, <value>)
# Example: ("👍", 10)
# Value can be negative to subtract authors EXP
# Example ("👎", -10)
# You can use custom emojis by it's name
# Example ("python_logo", 20)
EMOJIS=[
("👍", 10),
("👎", -10),
("python_logo", 20),
]

LEVELS=[
(1, 100),
(2, 250),
(3, 500),
(4, 1000),
(5, 1800),
]

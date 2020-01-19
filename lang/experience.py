
# No allowed variables
EXP_RESET = "Reseting all users experience. It will be calulated again in a moment..."
EXP_CALCULATION = "Calculating EXP for all users using messages from channels history..."
INITIALIZATION_DONE = "All calculations done."

# Allowed variables: {user_name} {user_exp} {user_level} {message_author}
LEVEL_COMMAND_RESPONSE = "{user_name} has {user_exp}EXP/-EXP. {user_name} is now on level {user_level}. Nice job!"

# Allowed variables: {user_name} {exp_got}/{exp_lost} {user_exp} {user_level} {reason}
USER_GOT_EXP = "{user_name} has got {exp_got}EXP {reason}. {user_name} has now {user_exp}EXP!"
USER_LOST_EXP = "{user_name} has lost {exp_lost}EXP {reason}. {user_name} has now {user_exp}EXP."

# Reasons. No allowed variables
FOR_WRITING_MESSAGE_REASON = "for writing a message"
FOR_MESSAGE_REMOVED_REASON = "because of his message removed"
FOR_GETTING_A_REACTION = "for getting a reaction"
FOR_LOSING_A_REACTION = "for losing a reaction"
FOR_REACTIONS_REMOVED = "beacuse of all reactions removed"

# Allowed variables: {message_author}
LEVEL_BOT_RESPONSE = "Sorry {author}! Levels are only for normal users."

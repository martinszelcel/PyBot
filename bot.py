from discord.ext.commands import Bot
from settings import DISCORD_TOKEN

bot = Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Logged as {bot.user}')

@bot.command()
async def reload(ctx):
    for extension in extensions:
        bot.reload_extension(extension)
    await ctx.send("All extensions reloaded.")

@bot.event
async def on_member_join(member):
    member.send(content="Welcome!")

@bot.event
async def on_member_update(before, after):
    if before.display_name != after.display_name:
        print(f"{before.name} changed his nickname to {after.display_name}")
        User.update(name=after.display_name).where(User.id == after.id).execute()

extensions = ['cogs.experience']

if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)

bot.run(DISCORD_TOKEN)

import discord
import sys, traceback
from discord.ext import commands
from settings import ADMIN_ROLE, ERROR_LOG_PM_USER_ID
from tokens import DISCORD_TOKEN

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Logged as {bot.user}')

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def reload(ctx):
    # Reload all extensions
    for extension in extensions:
        bot.reload_extension(extension)
    # Generate and send a embed
    embed = discord.Embed(title=":white_check_mark: All extensions was sucesfully reloaded!", color=0x0cc974)
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    # Generate embed with error message
    embed = discord.Embed(title=":warning: " + str(error), color=0xc95351)
    await ctx.send(embed=embed)

@bot.event
async def on_error(event, *args, **kwargs):
    # Generate error embed and send it to developer
    user = bot.get_user(ERROR_LOG_PM_USER_ID)
    embed = discord.Embed(title=f":broken_heart: Exception raised in {event} function.", color=0xc95351)
    type, value, tb = sys.exc_info()
    embed.add_field(name=f"{str(type)}    {str(value)}", value=''.join(traceback.format_exc()), inline=False)
    if len(str(*args)) > 0:
        embed.add_field(name="*args", value=str(*args), inline=False)
    if len(str(**kwargs)):
        embed.add_field(name="**kwargs", value=str(**kwargs), inline=False)
    await user.send(embed=embed)

@bot.event
async def on_raw_message_edit(payload):
    # If embed in a bot message was deleted, remove this message
    if "author" in payload.data.keys():
        author_id = int(payload.data["author"]["id"])
        embeds_count = len(payload.data["embeds"])
        content_length = len(payload.data["content"])

        if author_id == bot.user.id and embeds_count == 0 and content_length == 0:
            await bot.http.delete_message(payload.data["channel_id"], payload.data["id"])

@bot.event
async def on_member_update(before, after):
    # Update users name on change
    if before.display_name != after.display_name:
        print(f"{before.name} changed his nickname to {after.display_name}")
        User.update(name=after.display_name).where(User.id == after.id).execute()

extensions = ['cogs.ExperienceCog']

if __name__ == '__main__':
    for extension in extensions:
        bot.load_extension(extension)

    bot.run(DISCORD_TOKEN)

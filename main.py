import discord
import sys, traceback
from discord.ext import commands
from peewee import SqliteDatabase
from settings import ADMIN_ROLE, ERROR_LOG_PM_USER_ID, DATABASE
import configparser

bot = commands.Bot(command_prefix='!')
db = SqliteDatabase(DATABASE)

VERSION = "PyBot v0.0.1"

@bot.event
async def on_ready():
    print(f'Logged as {bot.user}')

@bot.command(name="reload")
@commands.has_role(ADMIN_ROLE)
async def reload(ctx):
    # Reload all extensions
    for extension in extensions:
        bot.reload_extension(extension)
    # Generate and send a embed
    embed = discord.Embed(title=":white_check_mark: All extensions was sucesfully reloaded!", color=0x0cc974)
    await ctx.send(embed=embed)

@bot.command(name="version", aliases=["v"])
async def version(ctx):
    embed = discord.Embed(title=f"Version: **{VERSION}**", color=0x0cc974)
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    # Generate embed with error message
    embed = discord.Embed(title=":warning: " + str(error), color=0xc95351)
    embed.set_footer(text=VERSION)
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
    embed.set_footer(text=VERSION)
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
    config = configparser.ConfigParser()
    config.read('TOKENS.INI')
    try:
        token = config.get('TOKENS', 'DISCORD_TOKEN')
        if token == "TOKEN_HERE":
            print("Please provide valid Discord bot token in TOKENS.INI file!")
            sys.exit()
    except configparser.NoSectionError:
        config.add_section('TOKENS')
    except configparser.NoSectionError:
        pass # fallback to next exception
    try:
        token = config.get('TOKENS', 'DISCORD_TOKEN')
    except configparser.NoOptionError:
            print("No Discord bot token found! Please place it in TOKENS.INI file, or paste it here:")
            token = input()
            with open('TOKENS.INI', 'w') as configfile:
                if len(token) > 0:
                    config.set('TOKENS', 'DISCORD_TOKEN', token)
                    config.write(configfile)
                else:
                    config.set('TOKENS', 'DISCORD_TOKEN', 'TOKEN_HERE')
                    config.write(configfile)
                    sys.exit()

    for extension in extensions:
        bot.load_extension(extension)

    bot.run(token)

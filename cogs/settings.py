import discord
from discord.ext import commands
from settings import ADMIN_ROLE, MESSAGE_EXP, ERROR_LOG_PM_USER_ID, ALLOWED_CHANNELS_ID, EMOJIS

class SettingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='settings')
    @commands.has_role(ADMIN_ROLE)
    async def settings(self, ctx, setting=None, value=None):
        embed = discord.Embed(title="Settings")

        if not setting:
            for cog_key in self.bot.cogs.keys():
                cog_settings = ""
                for cog in self.bot.cogs[cog_key]:
                    cog_setting += "Test"

                embed.add_field(name=f"**{cog}**", value=cog_settings")

                # embed.add_field(name=f"**{cog}**", value=f"""
                #     **Message exp:** *{MESSAGE_EXP}*
                #     **Error log user:** *{ERROR_LOG_PM_USER_ID}*
                #     **Allowed channels:** *{ALLOWED_CHANNELS_ID}*
                #     **Emojis:** *{EMOJIS}*
                # """)
        
        if setting == "msg_exp":
            embed.add_field(name="Message exp", value=f"Changed to {value}")

        print(self.bot.cogs)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(SettingsCog(bot))

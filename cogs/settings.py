import discord
from discord.ext import commands
from settings import ADMIN_ROLE, MESSAGE_EXP, ERROR_LOG_PM_USER_ID, ALLOWED_CHANNELS_ID, EMOJIS

class SettingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='settings')
    @commands.has_role(ADMIN_ROLE)
    async def level(self, ctx, *, setting: str=None):
        embed = discord.Embed()

        if not setting:
            embed.add_field(name="**Settigns**", value=f"""
                **Message exp:** *{MESSAGE_EXP}*
                **Error log user:** *{ERROR_LOG_PM_USER_ID}*
                **Allowed channels:** *{ALLOWED_CHANNELS_ID}*
                **Emojis:** *{EMOJIS}*
            """)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(SettingsCog(bot))

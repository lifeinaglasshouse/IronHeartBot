import discord
from discord.ext import commands

from ._openai import image
from common import check_none

class DallE(discord.Cog):
    
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
    
    @commands.command("image")
    async def image(self, ctx: commands.Context, *, prompt: str=None):
        """Generate image based on prompt"""
        if await check_none(prompt):
            return

        msg = await ctx.reply("**Generating Image**...")
        result = await image(prompt)
        
        await msg.edit(embed=discord.Embed(
            title=prompt
        ).set_image(url=result), content="")

def setup(bot: commands.Bot):
    bot.add_cog(DallE(bot))
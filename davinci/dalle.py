import discord
from discord.ext import commands

from ._openai import image

class DallE(discord.Cog):
    
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
    
    @commands.command("image")
    async def image(self, ctx: commands.Context, *, prompt: str):
        """Generate image based on prompt"""

        msg = await ctx.reply("**Generating Image**...")
        result = await image(prompt)
        
        await msg.edit(embed=discord.Embed(
            title=prompt
        ).set_image(url=result), content="")

def setup(bot: commands.Bot):
    bot.add_cog(DallE(bot))
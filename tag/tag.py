import discord
from discord.ext import commands

from .taginter import interpret, TagException

class Tag(discord.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    def cleanup_code(self, code: str):
        return code.strip().removeprefix('```').removesuffix('```').strip()
    
    @commands.command("run")
    async def run(self, ctx: commands.Context, *, code: str):
        try:
            await ctx.reply(f"**Output:**\n```\n{interpret(self.cleanup_code(code))[0] or '[NO OUTPUT]'}\n```")
        except TagException as e:
            await ctx.reply(f"**Error Occured:**\n```\n{e.args[0]}\n```")

def setup(bot: commands.Bot):
    bot.add_cog(Tag(bot))
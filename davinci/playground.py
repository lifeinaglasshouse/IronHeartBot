from discord import Cog, Message
from discord.ext import commands

from ._openai import completion
from common import check_none, text_to_fp

class Playground(Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.cnv_ctx: dict[int, str] = {} 
    
    async def send_result(self, msg: Message, result: str):
        if len(result) > 1990:
            await msg.edit(file=await text_to_fp("generated.txt", result))
        else:
            await msg.edit(f"```\n{result}\n```")
    
    @commands.command("wiki")
    async def wiki(self, ctx: commands.Context, *, about: str=None):
        """Generate fictional wiki"""
        if await check_none(ctx, about):
            return
        msg = await ctx.reply("**Generating...**")
        result = await completion(f"Write a fictional wiki about {about}:")
        await self.send_result(msg, result)
    
    @commands.command("completion")
    async def completion(self, ctx: commands.Context, *, prompt: str=None):
        """Generate completion from prompt"""
        if await check_none(ctx, prompt):
            return
        msg = await ctx.reply("**Generating...**")
        result = await completion(prompt)
        await self.send_result(msg, result)
    
    @commands.command("story")
    async def story(self, ctx: commands.Context, *, about: str=None):
        """Generate a story"""
        if await check_none(ctx, about):
            return
        msg = await ctx.reply("**Generating...**")
        result = await completion(f"Write a story about {about}:")
        await self.send_result(msg, result)
    
    @commands.command("conversation")
    async def conversation(self, ctx: commands.Context, *, who: str=None):
        """Start a conversation with someone"""
        if await check_none(ctx, who):
            return
        user = ctx.message.author
        msg = await ctx.reply("**Starting the conversation**")
        
        self.cnv_ctx[user.id] = f"This is a conversation between {user.name} and {who}."
        
        await msg.delete()
        await ctx.reply("Use `talk` command to talk with the person\nUse `end` command to end the conversation\nUse `current` to view the conversation")
    
    @commands.command("talk")
    async def talk(self, ctx: commands.Context, *, msg: str=None):
        """Talk in the current conversation"""
        if await check_none(ctx, msg):
            return
        if ctx.message.author.id not in self.cnv_ctx:
            await ctx.reply("You must use `conversation` command first!")
            return
        
        user = ctx.message.author
        
        if msg[-1] not in ("!",".","?"):
            msg += "."
        
        self.cnv_ctx[user.id] += f"\n{user.name}: {msg}\n"
        
        result = await completion(self.cnv_ctx[user.id])
        await ctx.reply(f"```\n{result}\n```")
        
        self.cnv_ctx[user.id] += "\n" + result
    
    @commands.command("action")
    async def action(self, ctx: commands.Context, *, event: str=None):
        """Add an event or context to the current conversation"""
        if await check_none(ctx, event):
            return
        if ctx.message.author.id not in self.cnv_ctx:
            await ctx.reply("You must use `conversation` command first!")
            return
        
        user = ctx.message.author
        
        if event[-1] != ".":
            event += '.'
        
        self.cnv_ctx[user.id] += "\n"+event
        
        await ctx.reply("Done. You can use `refresh` command or `talk` command")
    
    @commands.command("refresh")
    async def refresh(self, ctx: commands.Context):
        """Refresh current conversation"""
        if ctx.message.author.id not in self.cnv_ctx:
            await ctx.reply("You must use `conversation` command first!")
            return
        
        user = ctx.message.author
        
        result = await completion(self.cnv_ctx[user.id])
        await ctx.reply(f"```\n{result}\n```")
        
        self.cnv_ctx[user.id] += "\n" + result
    
    @commands.command("end")
    async def end(self, ctx: commands.Context):
        """End current conversation"""
        if ctx.message.author.id in self.cnv_ctx:
            del self.cnv_ctx[ctx.message.author.id]
            await ctx.reply("**Ending the conversation**")
        else:
            await ctx.reply("There is no conversation")
    
    @commands.command("current")
    async def current(self, ctx: commands.Context):
        """View current conversation context"""
        if ctx.message.author.id in self.cnv_ctx:
            r = self.cnv_ctx[ctx.message.author.id]
            if len(r) > 1990:
                await ctx.reply(file=text_to_fp("current.txt", r))
                return
            await ctx.reply(f"```\n{r}\n```")
        else:
            await ctx.reply("There is no conversation")

def setup(bot: commands.Bot):
    bot.add_cog(Playground(bot))
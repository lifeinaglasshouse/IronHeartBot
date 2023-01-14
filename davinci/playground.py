import discord
from discord import Cog, Message
from discord.ext import commands

from ._openai import completion
from common import check_none, text_to_fp
import re

tag_re = re.compile(r"<@([0-9]+[^>])>")

class Playground(Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.t_ctx: dict[int, str] = {}
        self.c_ctx: dict[int, str] = {}
    
    async def send_result(self, msg: Message, result: str):
        if len(result) > 1990:
            await msg.edit(file=await text_to_fp("generated.txt", result),
                           content="The generated is too large. sending in file")
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
    
    @commands.command("completion", aliases=["write"])
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
    
    @commands.command("gpthread")
    async def gpthread(self, ctx: commands.Context, *, prompt: str=None):
        """completion command but it will create thread and feed the gpt all messages there"""
        if await check_none(ctx, prompt):
            return
        user = ctx.message.author
        t: discord.Thread = await ctx.channel.create_thread(name=prompt,
                                                            message=ctx.message,
                                                            reason="penis")
        
        await t.add_user(user)
        
        self.t_ctx[t.id] = prompt
    
    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if message.channel.type == discord.ChannelType.public_thread:
            t = self.t_ctx.get(message.channel.id)
            if not t:
                return
            
            m = await message.reply("**Generating**")
            
            t += "\n\n"+message.clean_content
            
            result = await completion(t)
            
            self.t_ctx[message.channel.id] = t+"\n\n"+result
            
            await m.edit(result)

def setup(bot: commands.Bot):
    bot.add_cog(Playground(bot))
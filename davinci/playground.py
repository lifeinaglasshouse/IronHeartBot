import discord
from discord import Cog, Message
from discord.ext import commands

from ._openai import completion
from common import text_to_fp
from tinydb import TinyDB, Query

import os

class Playground(Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
        self.t_ctx: dict[int, str] = {}
        self.c_ctx: dict[int, str] = {}
        
        self.fp_db = TinyDB('db/template_prompt.db')
        self.fp_prefix = os.getenv("FP_PREFIX")
        if self.fp_prefix is None:
            raise Exception("FP_PREFIX key in .env not found")
        self.fp_q = Query()
    
    def new_template(self, name: str, f: str, author: int):
        self.fp_db.insert({
            "name": name,
            "author": author,
            "prompt": f
        })
    
    def get_template(self, name: str):
        return self.fp_db.get(self.fp_q.name == name)
    
    def rm_template(self, name: str, who: int):
        if self.get_template(name)["owner"] == who:
            self.fp_db.remove(self.fp_q.name == name)
            return True
        return False
    
    async def send_result(self, msg: Message, result: str):
        if len(result) > 1990:
            await msg.edit(file=await text_to_fp("generated.txt", result),
                           content="The generated text is too large. sending in file")
        else:
            await msg.edit(f"```\n{result}\n```")
    
    @commands.command("wiki")
    async def wiki(self, ctx: commands.Context, *, about: str):
        """Generate fictional wiki"""
        msg = await ctx.reply("**Generating...**")
        result = await completion(f"Write a fictional wiki about {about}:")
        await self.send_result(msg, result)
    
    @commands.command("completion", aliases=["write"])
    async def completion(self, ctx: commands.Context, *, prompt: str):
        """Generate completion from prompt"""
        msg = await ctx.reply("**Generating...**")
        result = await completion(prompt)
        await self.send_result(msg, result)
    
    @commands.command("story")
    async def story(self, ctx: commands.Context, *, about: str):
        """Generate a story"""
        msg = await ctx.reply("**Generating...**")
        result = await completion(f"Write a story about {about}:")
        await self.send_result(msg, result)
    
    @commands.command("gpthread")
    async def gpthread(self, ctx: commands.Context, *, prompt: str):
        """completion command but it will create thread and feed the gpt all messages there"""
        user = ctx.message.author
        t: discord.Thread = await ctx.channel.create_thread(name=prompt,
                                                            message=ctx.message,
                                                            reason="penis")
        
        await t.add_user(user)
        
        self.t_ctx[t.id] = prompt
    
    @commands.group(invoke_without_command=True)
    async def fprompt(self, ctx: commands.Context):
        await ctx.send("""
To create new fprompt:
```
    fprompt create <name> <format>
```
    Example
```
    fprompt create screenplay Write a screenplay about {}
    fprompt create JohnRickney Write a story about John and Rickney
```

To remove an existence fprompt:
```
    fprompt remove <name>
```
    _Note: You cannot delete other fprompt_

To invoke a fprompt:
```
    {prefix}<name> <argument>
```
    Example
```
    {prefix}screenplay The Jerma Show
```

To list all fprompt:
```
    fprompt list [user]
```
    _user is optional argument_
""".format("{}", prefix=self.fp_prefix))
    
    @fprompt.command("create")
    async def fp_create(self, ctx: commands.Context, name: str, *, format: str):
        if self.get_template(name):
            await ctx.reply(f"{name} fprompt already exist")
            return
        self.new_template(name, format, ctx.message.author.id)
        await ctx.reply(f"Successfully created {name}")
    
    @fprompt.command("remove")
    async def fp_remove(self, ctx: commands.Context, *, name: str):
        if not self.get_template(name):
            await ctx.reply(f"{name} fprompt not found")
            return
        if self.rm_template(name, ctx.message.author.id):
            return
        await ctx.reply(f"Failed to remove {name} (You're not the owner of this fprompt)")
    
    @fprompt.command("list")
    async def fp_list(self, ctx: commands.Context, user: discord.User=None):
        if user:
            r = self.fp_db.search(self.fp_q.author == user.id)
            if r:
                s = []
                for i, d in enumerate(r):
                    s.append("{}. {}".format(i+1, d["name"]))
                await ctx.reply("```\n{}\n```".format('\n'.join(s)))
            else:
                await ctx.reply("```\nthe user has not created any fprompt yet\n```")
            return
        
        r = self.fp_db.all()
        if not r:
            await ctx.reply("```\nNo fprompt has been created yet\n```")
        s = []
        for i, d in enumerate(r):
            _u = await self.bot.fetch_user(d["author"])
            s.append("{}. {} by {}".format(i+1, d["name"], _u.name))
        await ctx.reply("```\n{}\n```".format('\n'.join(s)))
    
    
    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if message.channel.type == discord.ChannelType.public_thread:
            t = self.t_ctx.get(message.channel.id)
            if not t:
                return
            
            if message.channel.archived is True:
                del self.t_ctx[message.channel.id]
                return
            
            if message.content.lower().startswith(f"!close"):
                await message.channel.archive(True)
                del self.t_ctx[message.channel.id]
                return
            
            m = await message.reply("**Generating**")
            
            t += "\n\n"+message.clean_content
            
            result = await completion(t)
            
            self.t_ctx[message.channel.id] = t+"\n\n"+result
            
            await m.edit(result)
            return
        
        if message.content.startswith(self.fp_prefix):
            c, a = message.content[len(self.fp_prefix):].split(maxsplit=1)
            
            fp = self.get_template(c)
            if not fp:
                await message.reply(f"No {c} fprompt found")
                return
            
            r: str = fp["prompt"].replace('{}', a)
            
            m = await message.reply("**Generating...**")
            
            result = await completion(r)
            
            await self.send_result(m, result)
            return

def setup(bot: commands.Bot):
    bot.add_cog(Playground(bot))
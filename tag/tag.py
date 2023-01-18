import discord
from discord.ext import commands

from .taginter import (interpret, TagException, tn_repr,
                       parse, TagInterpreter, TagStr)
from .tagdis import *
from .tagbuiltin import TagArray
from tinydb import TinyDB, Query

import re

discord_tag = re.compile(r"\<\@([0-9]+)\>")

class Tag(discord.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.tagdb = TinyDB('db/tag.db')
        self.tagq = Query()
        self.cache_code: dict[str, dict] = {}
    
    def get_tag(self, name: str):
        return self.tagdb.get(self.tagq.name == name)
    
    async def get_cache(self, ctx: commands.Context, name: str, code: str):
        if name in self.cache_code:
            return self.cache_code[name]
        return await self.new_cache(ctx, name, code)
    
    async def new_cache(self, ctx: commands.Context, name: str, code: str):
        try:
            self.cache_code[name] = parse(code)
            return self.cache_code[name]
        except TagException as e:
            await ctx.reply(f"**Error while parsing**\n```\n{e.args[0]}\n```")
            return None
    
    def cleanup_code(self, code: str):
        return code.strip().removeprefix('```').removesuffix('```').strip()
    
    @commands.command("run")
    async def run(self, ctx: commands.Context, *, code: str):
        try:
            r = interpret(self.cleanup_code(code))[0].v
            await ctx.reply(f"**Output:**\n```\n{tn_repr(r)}\n```")
        except TagException as e:
            await ctx.reply(f"**Error Occured:**\n```\n{e.args[0]}\n```")
    
    @commands.group(invoke_without_command=True)
    async def tag(self, ctx: commands.Context, name: str, *args: str):
        t = self.get_tag(name)
        if not t:
            await ctx.reply(f"No {name} tag found")
            return
        
        c = await self.get_cache(ctx, name, t['code'])
        if c is None:
            return
        
        a = []
        for arg in args:
            if (m := discord_tag.match(arg)):
                try:
                    a.append(TagUser(await self.bot.fetch_user(int(m.group(1)))))
                    continue
                except discord.NotFound:
                    pass
            a.append(TagStr(arg))
        
        i = TagInterpreter()
        i.import_dict({
            "User": tag_usertype,
            "user": TagUser(ctx.message.author),
            "args": TagArray(a)
        })
        
        try:
            r = i.visit(c).v
            await ctx.reply(tn_repr(r))
        except TagException as e:
            await ctx.reply(f"**Error Occured:**\n```\n{e.args[0]}\n```")
            return
    
    @tag.command('create')
    async def tag_create(self, ctx: commands.Context, name: str, *, code: str):
        if self.get_tag(name):
            await ctx.reply(f"tag {name} is already exist")
            return
        
        c = self.cleanup_code(code)
        
        if (await self.new_cache(ctx, name, c)) is None:
            return
        
        self.tagdb.insert({
            "name": name,
            "code": c,
            "author": ctx.message.author.id
        })
        
        await ctx.reply(f"Created tag {name}")
    
    @tag.command('remove')
    async def tag_rm(self, ctx: commands.Context, *, name: str):
        if not (t := self.get_tag(name)):
            await ctx.reply(f"tag {name} don't exist")
            return
        
        if t['author'] != ctx.message.author.id:
            if not ctx.message.author.guild_permissions.administrator():
                await ctx.reply(f"tag {name} is not owned by you")
                return
        
        self.tagdb.remove(doc_ids=[t.doc_id])
        await ctx.reply(f"Removed tag {name}")


def setup(bot: commands.Bot):
    bot.add_cog(Tag(bot))
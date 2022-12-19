import discord
from discord.ext import commands

class Info(discord.Cog):
    
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.cc: dict[str, list[commands.Command]] = {}
    
    def _cmd_fmt(self, cmd: commands.Command):
        return ""
    
    async def _update_cc(self):
        if "MAIN" not in self.cc:
            self.cc["MAIN"] = []
        for command in self.bot.commands:
            if not command.cog_name:
                self.cc["Main"].append(command)
            else:
                if command.cog_name not in self.cc:
                    self.cc[command.cog_name] = []
                self.cc[command.cog_name].append(command)
    
    @commands.command("help")
    async def help(self, ctx: commands.Context, *, cmdn: str=None):
        """Help command"""
        if not self.cc:
            await self._update_cc()
        
        p = await self.bot.get_prefix(ctx.message)
        
        if cmdn:
            cmd = self.bot.get_command(cmdn)
            if not cmd:
                await ctx.reply("No such command exist")
            else:
                a = ' '.join([f"<{n}>" for n in cmd.clean_params.keys()])
                await ctx.reply(f"```\n{p[0]}{cmdn} {a}\n\n\t{cmd.help or 'NO DESCRIPTION'}\n```")
            return
        
        s = f"```\n{self.bot.user.name} Command (prefix: {p[0]})\n\n"
        
        for cog_n, cmds in self.cc.items():
            s += cog_n + ":\n"
            for cmd in cmds:
                s += f"\t- {cmd.name}"
                if cmd.aliases:
                    s += f" ({', '.join(cmd.aliases)})"
                s += f"\n\t\t{cmd.help or 'NO DESCRIPTION'}\n"
            s += "\n"
        
        s = s.strip() + "\n```"
        
        await ctx.reply(s)

def setup(bot: commands.Bot):
    bot.add_cog(Info(bot))
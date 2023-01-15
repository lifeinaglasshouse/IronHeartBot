from discord import Embed, File
from discord.ext import commands
from io import StringIO

class BotError(Embed):
    
    def __init__(self, ctx: commands.Context, err: str, msg: str):
        super().__init__(
            title = err,
            description = f"An Error has occured\n```\n{msg}\n```",
            colour = 0xe83838
        )
        self.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

class InternalBotError(BotError):
    
    def __init__(self, ctx: commands.Context, err: str, msg: str):
        super().__init__(ctx, err, msg)
        self.set_footer(text="This is bot fault")

class UserBotError(BotError):
    
    def __init__(self, ctx: commands.Context, err: str, msg: str):
        super().__init__(ctx, err, msg)
        self.set_footer(text="This is user fault")

async def text_to_fp(filename: str, txt: str):
    f = StringIO(txt)
    return File(fp=f, filename=filename)
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from common import InternalBotError, UserBotError

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=(";", "; "), intents=intents, help_command=None)

bot.load_extensions(*(
    "davinci.playground",
    "core.info"
))

@bot.event
async def on_ready():
    print("ready")

@bot.event
async def on_command_error(ctx: commands.Context, err: Exception):
    if isinstance(err, commands.CommandNotFound):
        await ctx.reply(embed=UserBotError(ctx, "CommandNotFound", err.args[0]))
        return
    await ctx.reply(embed=InternalBotError(ctx, err.__class__.__name__, ','.join(err.args)))
    raise err

bot.run(TOKEN)
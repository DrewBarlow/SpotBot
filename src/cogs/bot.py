from __future__ import annotations
from discord.ext import commands
import discord

class SpotBot(commands.Cog):
    def __init__(self: SpotBot, bot: commands.Bot) -> None:
        self._bot: commandsBot = bot
        return

    @Cog.listener()
    async def on_message(self: SpotBot, message: discord.Message) -> None:
        print("test")
        return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SpotBot(bot))
    return


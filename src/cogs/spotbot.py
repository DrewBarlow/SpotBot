from __future__ import annotations
from discord.ext import commands
from discord import app_commands
import discord

class SpotBot(commands.Cog, name="spotbot"):
    def __init__(self: SpotBot, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

        super().__init__()
        return

    @commands.Cog.listener()
    async def on_message(self: SpotBot, message: discord.Message) -> None:
        return

    @app_commands.command(name="test")
    async def _test(self: SpotBot, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Test SpotBot Cog")
        return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SpotBot(bot))
    return


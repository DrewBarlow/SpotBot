from __future__ import annotations
from discord.ext import commands
from discord import app_commands
import discord

class Spotify(commands.Cog, name="spotify"):
    def __init__(self: Spotify, bot: commands.Bot) -> None:
        self._bot = commands.Bot = bot

        super().__init__()
        return

    @commands.Cog.listener()
    async def on_message(self: Spotify, message: discord.Message) -> None:
        return

    @app_commands.command(name="test2")
    async def _test(self: Spotify, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Test Spotify Cog")
        return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Spotify(bot))
    return


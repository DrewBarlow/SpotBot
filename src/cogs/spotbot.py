from __future__ import annotations
from discord.ext import commands
from discord import app_commands
from os import getenv
from .spotifyinteraction import SpotifyInteraction
import discord

class SpotBot(commands.Cog, name="spotbot"):
    __debug_on: bool = bool(int(getenv("DEBUG")))
    def __init__(self: SpotBot, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
        self._spotify: SpotifyInteraction = SpotifyInteraction()

        super().__init__()
        return

    @app_commands.command(name="togglevoting")
    async def _toggle_voting(self: SpotBot, interaction: discord.Interaction) -> None:
        self._spotify.toggle_voting()

        msg: str = ""
        if self._spotify.is_voting():
            msg = "Voting has been enabled!"
        else:
            msg = "Voting has been disabled!"

        await interaction.response.send_message(msg, ephemeral=self.__debug_on)
        return

    @app_commands.command(name="showplaylist")
    async def _show_playlist(self: SpotBot, interaction: discord.Interaction) -> None:
        tracks: list[tuple[str, str, str]] = self._spotify.get_tracks()
        playlist_info: tuple[str, str] = self._spotify.get_weekly_playlist_info()

        tracks_msg: str = "```\n"
        for i, track in enumerate(tracks):
            name: str = track[0]
            artist_name: str = track[1]
            tracks_msg += f"{i + 1}. {name} - {artist_name}\n"
            print(tracks_msg)
        tracks_msg += "```"

        embed: discord.Embed = discord.Embed(
            title=playlist_info[0],
            description=tracks_msg
        ).set_thumbnail(url=playlist_info[1])

        await interaction.response.send_message(embed=embed, ephemeral=self.__debug_on)
        return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SpotBot(bot))
    return

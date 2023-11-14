from __future__ import annotations
from discord.ext import commands
from discord import app_commands
from os import getenv

from discord.webhook.async_ import interaction_response_params
from spotifyinteraction import SpotifyInteraction
from typing import Optional
import discord

class SpotBot(commands.Cog, name="spotbot"):
    def __init__(self: SpotBot, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
        self._spotify: SpotifyInteraction = SpotifyInteraction()
        self._votes: dict[discord.User|discord.Member, str] = {}

        super().__init__()
        return

    @app_commands.command(
        name="whovoted",
        description="Call out the mfs who didn't vote."
    )
    async def _who_voted(self: SpotBot, interaction: discord.Interaction) -> None:
        if not self._spotify.is_voting():
            await interaction.response.send_message("Voting hasn't started.")

        desc: str = ""
        for user in self._votes:
            desc += f"- {user.display_name}\n"

        embed: discord.Embed = discord.Embed(
            title="The people that voted.",
            description=desc
        )

        await interaction.response.send_message(embed=embed)
        return

    async def _tally_votes(self: SpotBot) -> tuple[str, discord.Embed]:
        msg: str = ""

        songs_and_votes: dict[str, int] = {}
        for song in self._votes.values():
            if songs_and_votes.get(song) is None:
                songs_and_votes[song] = 0

            songs_and_votes[song] += 1

        ordered_votes: list[tuple[str, int]] = list(songs_and_votes.items())
        ordered_votes.sort(key=lambda tup: tup[1])

        is_tie: bool = False
        if len(ordered_votes) > 1:
            first_place: tuple[str, int] = ordered_votes[0]
            second_place: tuple[str, int] = ordered_votes[1]
            is_tie = first_place[1] == second_place[1]

            if is_tie:
                msg = "There's a tie."
                self._spotify.toggle_voting()

        if not is_tie:
            msg = f"{ordered_votes[0][0]} wins."
            self._votes = {}
            await self._bot.change_presence(activity=None)

        desc: str = "```\n"
        for song, votes in ordered_votes: 
            desc += f"{votes} | {song}"
        desc += "```"

        embed = discord.Embed(
            title="Results",
            description=desc
        )

        return msg, embed

    @app_commands.command(
        name="togglevoting",
        description="Turn voting on or off."
    )
    async def _toggle_voting(self: SpotBot, interaction: discord.Interaction) -> None:
        self._spotify.toggle_voting()
        msg: str = ""
        embed: Optional[discord.Embed] = None

        if self._spotify.is_voting():
            msg = "Voting has been enabled!"
            await self._bot.change_presence(activity=discord.Game(name="Voting is open!"))
        else:
            if len(self._votes) > 0:
                msg, embed = await self._tally_votes()
            else:
                msg = "Voting has been disabled"

        await interaction.response.send_message(msg, embed=embed)
        return

    @app_commands.command(
        name="vote",
        description="Vote for a song this week."
    )
    async def _vote(self: SpotBot, interaction: discord.Interaction) -> None:
        if not self._spotify.is_voting():
            await interaction.response.send_message("Voting isn't active.")
            return

        options: list[discord.SelectOption] = [
            discord.SelectOption(
                label=(f"{track[0]} - {track[1]}"[:100])
            ) for track in self._spotify.get_tracks()
        ]
        view: discord.ui.View = discord.ui.View()
        select: discord.ui.Select = discord.ui.Select(options=options)

        async def callback(interaction: discord.Interaction) -> None:
            self._votes[interaction.user] = select.values[0]
            await interaction.response.send_message(f"You voted for {select.values[0]}.", ephemeral=True)
            return

        select.callback = callback
        view.add_item(select)
        await interaction.response.send_message("Vote!", view=view, ephemeral=True)
        return

    # @app_commands.command(name="updateplaylist")
    # async def _update_playlist(self: SpotBot, interaction: discord.Interaction) -> None:
    #     await interaction.response.send_modal(WinnerModal())
    #     return

    @app_commands.command(
        name="showplaylist",
        description="Dumps the current weekly playlist in chat."
    )
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

        await interaction.response.send_message(embed=embed)
        return


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SpotBot(bot))
    return

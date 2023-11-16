from __future__ import annotations
from discord.ext import commands
from discord import app_commands
from spotifyinteraction import SpotifyInteraction
from typing import Optional
import discord

class SpotBot(commands.Cog, name="spotbot"):
    def __init__(self: SpotBot, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
        self._spotify: SpotifyInteraction = SpotifyInteraction()
        self._votes: dict[discord.User|discord.Member, str] = {}
        self._is_tie: bool = False
        self._tied_songs: list[str] = []

        super().__init__()
        return

    @app_commands.command(
        name="whovoted",
        description="Call out the mfs who didn't vote."
    )
    async def _who_voted(self: SpotBot, interaction: discord.Interaction) -> None:
        """
        Display who voted this week.
        """
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

    def _order_votes(self: SpotBot) -> list[tuple[str, int]]:
        """
        Enumerates over self._votes and returns a list of tuples that looks like
            [("song1", num_votes1), ("song2", num_votes2), ...]
        """
        # count up how many times each song was voted for
        songs_and_votes: dict[str, int] = {}
        for song in self._votes.values():
            if songs_and_votes.get(song) is None:
                songs_and_votes[song] = 0

            songs_and_votes[song] += 1

        # sort which songs have the most votes
        ordered_votes: list[tuple[str, int]] = list(songs_and_votes.items())
        ordered_votes.sort(key=lambda tup: tup[1])

        return ordered_votes

    def _tally_votes(self: SpotBot) -> Optional[discord.Embed]:
        """
        Counts the votes and determines if there is a tie.
        Returns an embed with necessary information
        """
        embed: Optional[discord.Embed] = None
        ordered_votes: list[tuple[str, int]] = self._order_votes()

        # take into account if only one vote is present when voting
        # ends which should not happen
        if len(ordered_votes) > 1:
            last_song: tuple[str, int] = ("", 0)
            for (song, votes) in ordered_votes:
                # if we are at the first song, skip it
                if song == ordered_votes[0][0]:
                    last_song = (song, votes)
                    self._tied_songs = [song]
                    continue
                
                # if the number of votes matches the last song's,
                # we have a tie. iterate over all songs to gather
                # which songs are tied for a win
                if votes == last_song[1]:
                    self._is_tie = True
                    last_song = (song, votes)
                    self._tied_songs.append(song)

                # if we iterate over all songs, songs that lost
                # but still have the same number of votes will
                # be counted too. avoid this by stopping the loop
                else:
                    break

            if self._is_tie:
                self._spotify.toggle_voting()
                self._votes = {}
            else:
                self._tied_songs = []
        else:
            self._is_tie = False
            self._tied_songs = []
            self._votes = {}

        return self._make_vote_embed(ordered_votes)

    def _make_vote_embed(self: SpotBot, ordered_votes: list[tuple[str, int]]) -> discord.Embed:
        """
        Creates an embed with necessary voting results information and returns it.
        """
        embed: discord.Embed = discord.Embed()
        desc: str = "```\n"
        for song, votes in ordered_votes: 
            desc += f"{votes} | {song}\n"
        desc += "```"

        if not self._is_tie:
            # for (song, artist, album_url) in self._spotify.get_tracks():
            #     song_and_artist: str = f"{song} - {artist}"
            #
            #     if song_and_artist == ordered_votes[0][0]:
            embed = discord.Embed(
                title=ordered_votes[0][0],
                description=desc
            )
                    # ).set_thumbnail(album_url)
                    # break

            self._votes = {}
        else:
            embed = discord.Embed(
                title="Tie!",
                description=desc
            )

        return embed

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
            # take into account if no votes are present when voting ends, which
            # should not happen
            if len(self._votes) > 0:
                embed = self._tally_votes()

            if not self._is_tie:
                msg = "Voting has been disabled."
                await self._bot.change_presence(activity=discord.Game(name="Voting is closed."))

        await interaction.response.send_message(msg, embed=embed)
        return

    @app_commands.command(
        name="vote",
        description="Vote for a song this week."
    )
    async def _vote(self: SpotBot, interaction: discord.Interaction) -> None:
        """
        Allows a user to vote for a song in the playlist or a tied song.
        """
        if not self._spotify.is_voting():
            await interaction.response.send_message("Voting isn't active.")
            return

        # create a list of tracks we can vote for
        tracks_list: list[str] = []
        if self._is_tie:
            tracks_list = self._tied_songs
        else:
            tracks_list = [f"{track[0]} - {track[1]}"[:100] for track in self._spotify.get_tracks()]

        # turn the tracks into options and add them to a dropdown view
        options: list[discord.SelectOption] = [discord.SelectOption(label=track) for track in tracks_list]
        view: discord.ui.View = discord.ui.View()
        select: discord.ui.Select = discord.ui.Select(options=options)

        async def callback(interaction: discord.Interaction) -> None:
            self._votes[interaction.user] = select.values[0]
            await interaction.message.edit_message(f"You voted for {select.values[0]}.", ephemeral=True)
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
        """
        Query the Spotify API and show all songs in the current playlist.
        """
        tracks: list[tuple[str, str, str]] = self._spotify.get_tracks()
        playlist_info: tuple[str, str] = self._spotify.get_weekly_playlist_info()

        tracks_msg: str = "```\n"
        for i, track in enumerate(tracks):
            name: str = track[0]
            artist_name: str = track[1]
            tracks_msg += f"{i + 1}. {name} - {artist_name}\n"
            print(tracks_msg)
        tracks_msg += "```"

        # create an embed representation of the current playlist state
        embed: discord.Embed = discord.Embed(
            title=playlist_info[0],
            description=tracks_msg
        ).set_thumbnail(url=playlist_info[1])

        await interaction.response.send_message(embed=embed)
        return


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SpotBot(bot))
    return

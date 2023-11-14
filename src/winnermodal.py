from __future__ import annotations
from discord import ui
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import discord

class WinnerModal(ui.Modal, title="Playlist Update"):
    new_playlist_name: ui.TextInput = ui.TextInput(label="New Playlist Name", required=True)
    new_playlist_image: ui.TextInput = ui.TextInput(label="New Playlist Image (URL)", required=True)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        spotify: Spotify = Spotify(client_credentials_manager=SpotifyClientCredentials())
        await interaction.response.send_message(f"New theme: {new_playlist_name}.", ephemeral=True)
        return


from __future__ import annotations
from aiohttp import ClientSession
from base64 import b64encode
from discord import ui
from io import BytesIO
from PIL import Image
from spotifyinteraction import SpotifyInteraction
import discord

class WinnerModal(ui.Modal, title="Playlist Update"):
    new_playlist_name: ui.TextInput = ui.TextInput(label="New Playlist Name", required=True)
    new_playlist_image: ui.TextInput = ui.TextInput(label="New Playlist Image (URL)", required=True)

    # untested
    async def on_submit(self, interaction: discord.Interaction) -> None:
        spotify: SpotifyInteraction = SpotifyInteraction()

        # fetch the image
        img: bytes = b""
        async with ClientSession() as session:
            async with session.get(self.new_playlist_image) as resp:
                img = await resp.read()

        # convert to JPEG
        pil_img: Image.Image = Image.frombuffer("RGBA", (128, 128), img)
        pil_img = pil_img.convert("RGB")

        # write to bytes and b64 encode
        img_arr = BytesIO()
        pil_img.save(img_arr, format="JPEG")
        img = img_arr.getvalue()
        img = b64encode(img)

        # update the playlist
        await spotify.update_weekly_playlist(self.new_playlist_image, img.decode())
        await interaction.response.send_message(f"New theme: {self.new_playlist_name}.", ephemeral=True)
        return


from __future__ import annotations
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Optional

class SpotifyInteraction():
    _MENTLEGEN_URI: str = "spotify:playlist:7LHEhLc92p5gtorCRwXOEd"
    _WEEKLY_URI: str = "spotify:playlist:29NEM3UYqF1KBjD92vUUGd"

    def __init__(self: SpotifyInteraction) -> None:
        self._spotify: Spotify = Spotify(client_credentials_manager=SpotifyClientCredentials())
        self._is_voting: bool = False

        super().__init__()
        return

    def get_spotify(self: SpotifyInteraction) -> Spotify:
        return self._spotify

    def toggle_voting(self: SpotifyInteraction) -> None:
        self._is_voting = not self._is_voting
        return

    def is_voting(self: SpotifyInteraction) -> bool:
        return self._is_voting

    def get_weekly_playlist_info(self: SpotifyInteraction) -> tuple[str, str]:
        """
        Returns: A tuple with the playlist name and covert art url.
        """
        weekly_playlist_info: tuple[str, str] = ("", "")

        weekly_playlist: Optional[dict] = self._spotify.playlist(self._WEEKLY_URI)
        if weekly_playlist:
            playlist_name: str = weekly_playlist["name"]
            playlist_image_url: str = weekly_playlist["images"][0]["url"]

            weekly_playlist_info = (playlist_name, playlist_image_url)

        return weekly_playlist_info

    def get_tracks(self: SpotifyInteraction) -> list[tuple[str, str, str]]:
        """
        Returns: A list of tuples that look like the following-
                 (track_name, artist_name, album_cover_url)
        """
        tracks: list[tuple[str, str, str]] = []

        weekly_playlist_items: Optional[dict] = self._spotify.playlist_items(self._WEEKLY_URI)
        if weekly_playlist_items:
            for track in weekly_playlist_items["items"]:
                track_name: str = track["track"]["name"]
                artist_name: str = track["track"]["artists"][0]["name"]
                album_cover_url: str = track["track"]["album"]["images"][0]["url"]

                tracks.append((track_name, artist_name, album_cover_url))

        return tracks

    def update_weekly_playlist(self: SpotifyInteraction, new_name: str, new_image_url: str) -> None:
        """
        Migrates all songs from weekly to master and updates details
        of the weekly playlist.
        """
        self._spotify.playlist_change_details(self._WEEKLY_URI, name=new_name)
        # self._migrate_songs_from_weekly()
        return

    def _migrate_songs_from_weekly(self: SpotifyInteraction) -> None:
        """
        Removes all songs from the weekly playlist and adds them
        to the master playlist.
        """
        track_uris: list[str] = []

        weekly_playlist_items: Optional[dict] = self._spotify.playlist_items(self._WEEKLY_URI)
        if weekly_playlist_items:
            for track in weekly_playlist_items["items"]:
                track_uris.append(track)

        self._spotify.playlist_add_items(self._MENTLEGEN_URI, track_uris)
        self._spotify.playlist_remove_all_occurrences_of_items(self._WEEKLY_URI, track_uris)

        return


import sys
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import csv


scope = 'user-rlibrary-read'

# https://developer.spotify.com/dashboard
client_id = 'YOUR ID'
client_secret = 'YOUR SECRET'
redirect_uri = 'https://developer.spotify.com/documentation/web-api/'

# https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile
username = 'YOUR USERNAME'

# Set up authentication
scope = "user-library-read"  # Example scope, you can change this according to your needs
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))

with open("SpotifyData.csv", "w", newline='') as file:
    writer = csv.writer(file)
    # Write header
    writer.writerow(["Name", "URI", "Artist", "Release Year", "Genre", "Danceability", "Energy", "Key", "Loudness", "Mode", "Speechiness",
                     "Acousticness", "Instrumentalness", "Liveness", "Valence", "Tempo", "Duration_ms", "Time_Signature"])

    # Example: Get the user's saved tracks
    results = sp.current_user_saved_tracks(limit = 50)
    idxCount = 0
    while results:
        for idx, item in enumerate(results['items']):
            track = item['track']
            uri = track['uri']
            audioFeat = sp.audio_features(uri)[0]

            # Get the artist name and ID (assuming the first artist)
            artist = track['artists'][0]
            artist_name = artist['name']
            artist_id = artist['id']

            # Get artist details to fetch genre
            artist_info = sp.artist(artist_id)
            genre = artist_info['genres']
            genre_str = ", ".join(genre) if genre else "Unknown"  # Convert list to a string or use "Unknown"

            # Get the release year
            release_year = track['album']['release_date'][:4]  # The first 4 characters are the year

            print(idxCount + idx, track['name'], " - ", artist_name, " - ", release_year, " - ", genre_str, " - ", uri, " - ", audioFeat)

        
        # Write data to CSV
            writer.writerow([track['name'], track['uri'], artist_name, release_year, genre_str, audioFeat['danceability'],
                             audioFeat['energy'], audioFeat['key'], audioFeat['loudness'],
                             audioFeat['mode'], audioFeat['speechiness'], audioFeat['acousticness'],
                             audioFeat['instrumentalness'], audioFeat['liveness'], audioFeat['valence'],
                             audioFeat['tempo'], audioFeat['duration_ms'], audioFeat['time_signature']])


        idxCount += len(results['items'])
        # Check if there are more pages of saved tracks
        if results['next']:
            results = sp.next(results)
        else:
            results = None

import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

# Spotify API credentials (replace with your own credentials)
CLIENT_ID = "711df9faaba8446e8a9a95176c173320"
CLIENT_SECRET = "736e6c5c59ec441697359c7278e1a343"
REDIRECT_URI = "http://localhost:8888/callback"

# Spotipy authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-library-read user-top-read"
))

def rate_limited_fetch(api_call, *args, **kwargs):
    """
    Executes an API call with rate-limiting.
    Adds a delay if a rate limit error (HTTP 429) is encountered.
    """
    while True:
        try:
            response = api_call(*args, **kwargs)
            return response
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get("Retry-After", 1))
                print(f"Rate limit reached. Retrying in {retry_after} seconds...")
                time.sleep(retry_after + 1)  # Sleep for the retry period
            else:
                raise e

def search_song(query):
    """Search for a song on Spotify."""
    results = rate_limited_fetch(sp.search, q=query, type="track", limit=1)
    if results['tracks']['items']:
        song = results['tracks']['items'][0]
        return {
            "track_name": song['name'],
            "artist": song['artists'][0]['name'],
            "album": song['album']['name'],
            "id": song['id'],
            "popularity": song['popularity']
        }
    else:
        print("No results found for your search query.")
        return None

def fetch_recommendations(seed_tracks):
    """Fetch recommendations based on seed tracks."""
    recommendations = rate_limited_fetch(sp.recommendations, seed_tracks=seed_tracks, limit=10)
    tracks = []
    for item in recommendations['tracks']:
        tracks.append({
            "track_name": item['name'],
            "artist": item['artists'][0]['name'],
            "album": item['album']['name'],
            "id": item['id'],
            "popularity": item['popularity']
        })
    return pd.DataFrame(tracks)

def main():
    # Step 1: Search for a specific song
    query = input("Enter the song name or keywords to search for: ")
    song = search_song(query)
    if not song:
        return

    print("\nSearch Result:")
    print(f"Track: {song['track_name']}\nArtist: {song['artist']}\nAlbum: {song['album']}")
    
    # Step 2: Fetch recommendations based on the searched song
    print("\nFetching recommendations based on this song...")
    recommendations = fetch_recommendations([song['id']])
    print("\nRecommended Songs:")
    if recommendations.empty:
        print("No recommendations found.")
    else:
        print(recommendations[['track_name', 'artist', 'album']])

if __name__ == "__main__":
    main()

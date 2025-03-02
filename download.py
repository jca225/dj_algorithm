"""pip install yt-dlp"""
"""Must install ffmpeg as well"""

import yt_dlp
import urllib.parse
import os

# Define a directory for downloaded songs
DOWNLOAD_DIR = "downloads"

# Create the directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

### Initial script to download a song off of youtube given its name and artist ###
def download_song(artist, song_name):
    query = f"{artist} {song_name} audio"
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"

    # Define the output path inside the downloads folder
    output_template = os.path.join(DOWNLOAD_DIR, f"{song_name} - {artist}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_template,  # Save in downloads directory
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '160',
        }],
        'noplaylist': True,  # Avoid playlists
        'fragment_retries': 3, #retry fragments a few times.
        'concurrent_fragments': 8, #download 8 fragments at a time.
        'quiet': False,  # Show progress

    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Use ytsearch1: to get the first relevant result
            video_url = f"ytsearch1:{query}"
            ydl.download([video_url])
            print(f"Downloaded: {song_name} - {artist} to {DOWNLOAD_DIR}/")
        except yt_dlp.utils.DownloadError:
            print("Error downloading song. Try a different query.")


if __name__ == "__main__":
    artist = input("Enter the artist's name: ")
    song_name = input("Enter the song's name: ")
    
    download_song(artist, song_name)
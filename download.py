import os
import yt_dlp
from pathlib import Path

def download_youtube_audio(url: str):
    downloads_path = str(Path.home() / "Downloads")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(downloads_path, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"📥 Скачиваем {url} в MP3...")
        ydl.download([url])
        print(f"✅ Скачано в: {downloads_path}")

if __name__ == "__main__":
    youtube_url = input("ссылка на ютуб: ").strip()
    download_youtube_audio(youtube_url)

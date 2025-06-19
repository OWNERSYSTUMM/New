import re
import requests
from pyrogram import filters

from SystemMusic import app
from config import LOGGER_ID


@app.on_message(filters.regex(r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/.*$"))
async def download_instagram_video(client, message):
    url = message.text
    a = await message.reply_text("Processing...")
    
    api_url = f"https://insta-dl.hazex.workers.dev/?url={url}"

    response = requests.get(api_url)
    try:
        result = response.json()
        data = result["result"]
    except Exception as e:
        f = f"Error :\n{e}"
        try:
            await a.edit(f)
        except Exception:
            await message.reply_text(f)
            return await app.send_message(LOGGER_ID, f)
        return await app.send_message(LOGGER_ID, f)
    
    if not result["error"]:
        video_url = data["url"]
        duration = data["duration"]
        quality = data["quality"]
        type = data["extension"]
        size = data["formattedSize"]
        caption = f"Duration : {duration}\nQuality : {quality}\nType : {type}\nSize : {size}"
        await a.delete()
        await message.reply_video(video_url, caption=caption)
    else:
        try:
            return await a.edit("Failed to download reel")
        except Exception:
            return await message.reply_text("Failed to download reel")


MODULE = "Reel"
HELP = """
Instagram reel downloader:

Simply send the Instagram reel URL to download the video.
"""

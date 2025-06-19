import asyncio
import re
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError
import logging
import urllib.parse
from datetime import datetime
from SystemMusic import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

# Instagram URL pattern
INSTA_REEL_PATTERN = r"https?://(?:www\.)?instagram\.com/(?:reel|reels|p)/([A-Za-z0-9_-]+)"

async def download_progress(current, total, message: Message, start_time):
    """Callback to show download progress"""
    try:
        percentage = (current / total) * 100
        elapsed = datetime.now().timestamp() - start_time
        if elapsed > 1:  # Update every second
            await message.edit_text(f"Downloading... {percentage:.1f}%")
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception:
        pass

async def get_reel_url(insta_link: str) -> str:
    """Scrape Instagram page to extract reel video URL"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(insta_link, headers=headers, timeout=10) as response:
                if response.status != 200:
                    logger.error(f"HTTP {response.status} for {insta_link}")
                    return None
                html = await response.text()
                
                # Look for video URL in HTML
                video_url_match = re.search(r'"video_url":"(https?://[^"]+\.mp4[^"]*)"', html)
                if video_url_match:
                    video_url = video_url_match.group(1)
                    # Unescape URL
                    video_url = urllib.parse.unquote(video_url)
                    return video_url
                else:
                    logger.warning(f"No video URL found in {insta_link}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {insta_link}: {str(e)}")
            return None

@app.on_message(filters.command(["start"]))
async def start_command(client, message: Message):
    """Handle /start command"""
    await message.reply_text(
        "Hi! I'm an Instagram Reel Downloader Bot.\n"
        "Send me an Instagram Reel link, and I'll download the video for you.\n"
        "Use /help for more info."
    )

@app.on_message(filters.command(["help"]))
async def help_command(client, message: Message):
    """Handle /help command"""
    await message.reply_text(
        "To download an Instagram Reel:\n"
        "1. Copy the Reel link from Instagram (e.g., https://www.instagram.com/reel/ABC123/).\n"
        "2. Send the link to me.\n"
        "3. Wait for the video to be downloaded and sent back.\n\n"
        "Note: Only public Reels can be downloaded. Private posts or invalid links won't work."
    )

@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def handle_message(client, message: Message):
    """Handle Instagram Reel links"""
    insta_link = message.text.strip()
    
    # Validate Instagram Reel URL
    if not re.match(INSTA_REEL_PATTERN, insta_link):
        await message.reply_text("Please send a valid Instagram Reel link (e.g., https://www.instagram.com/reel/ABC123/).")
        return
    
    # Send initial message
    status_msg = await message.reply_text("Processing your Reel link...")
    
    try:
        # Get video URL
        video_url = await get_reel_url(insta_link)
        if not video_url:
            await status_msg.edit_text("Sorry, I couldn't find a video in this Reel. It might be private or invalid.")

return
        
        # Update status
        await status_msg.edit_text("Downloading Reel video...")
        
        # Download and send video
        start_time = datetime.now().timestamp()
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as response:
                if response.status != 200:
                    await status_msg.edit_text("Failed to download the video. Please try again later.")
                    return
                
                # Stream video to Telegram
                await message.reply_video(
                    video_url,
                    progress=download_progress,
                    progress_args=(message, start_time),
                    caption=f"Downloaded from: {insta_link}"
                )
                
                # Delete status message
                await status_msg.delete()
                
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await status_msg.edit_text(f"Rate limited. Retrying after {e.value} seconds...")
        await handle_message(client, message)  # Retry
    except RPCError as e:
        logger.error(f"Telegram RPC Error: {str(e)}")
        await status_msg.edit_text("An error occurred while sending the video. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        await status_msg.edit_text("An unexpected error occurred. Please try again or contact support.")

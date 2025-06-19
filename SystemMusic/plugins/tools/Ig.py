import asyncio,re,aiohttp
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from SystemMusic import app
from datetime import datetime
INSTA_REEL=r"https?://(?:www\.)?instagram\.com/(?:reel|reels|p)/([A-Za-z0-9_-]+)"
async def progress(c,t,m,s):
 try:
  if datetime.now().timestamp()-s>1:await m.edit(f"Downloading... {c/t*100:.1f}%")
 except:pass
async def get_url(l):
 async with aiohttp.ClientSession() as s:
  async with s.get(l,headers={"User-Agent":"Mozilla/5.0"},timeout=10)as r:
   if r.status!=200:return None
   h=await r.text()
   m=re.search(r'"video_url":"(https?://[^"]+\.mp4[^"]*)"',h)
   return m.group(1).replace("\/", "/")if m else None
@app.on_message(filters.text)
async def h(_,m:Message):
 l=m.text.strip()
 if not re.match(INSTA_REEL,l):
  await m.reply("Send a valid Instagram Reel link\nHi! Send me an Instagram Reel link to download the video.")
  return
 s=await m.reply("Processing...")
 try:
  v=await get_url(l)
  if not v:await s.edit("Couldn't find video. It might be private.");return
  await s.edit("Downloading...")
  await m.reply_video(v,progress=progress,progress_args=(m,datetime.now().timestamp()),caption=f"From: {l}")
  await s.delete()
 except FloodWait as e:
  await asyncio.sleep(e.value)
  await h(_,m)
 except:await s.edit("Error occurred. Try again.")

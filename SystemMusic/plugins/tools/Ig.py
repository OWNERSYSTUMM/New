from pyrogram import filters
from SystemMusic import app
import bs4, requests, re, asyncio, os, random

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Length": "99",
    "Origin": "https://saveig.app",
    "Connection": "keep-alive",
    "Referer": "https://saveig.app/en",
}

@app.on_message(filters.regex(r'https?://.*instagram[^\s]+') & filters.incoming)
async def link_handler(_, message):
    link = message.matches[0].group(0)
    try:
        m = await message.reply_sticker("CAACAgIAAxkBATWhF2Qz1Y-FKIKqlw88oYgN8N82FtC8AAJnAAPb234AAT3fFO9hR5GfHgQ")
        url = link.replace("instagram.com", "ddinstagram.com").replace("==", "%3D%3D")
        video_url = url[:-1] if url.endswith("=") else url
        dump_file = await message.reply_video(video_url, caption="Thank you for using our bot!")
        await m.delete()
    except Exception:
        try:
            if "/reel/" in link:
                ddinsta = True
                getdata = requests.get(url).text
                soup = bs4.BeautifulSoup(getdata, 'html.parser')
                meta_tag = soup.find('meta', attrs={'property': 'og:video'})
                if meta_tag:
                    content_value = f"https://ddinstagram.com{meta_tag['content']}"
                else:
                    ddinsta = False
                    meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
                    if meta_tag.ok:
                        res = meta_tag.json()
                        meta = re.findall(r'href="(https?://[^"]+)"', res['data'])
                        content_value = meta[0]
                    else:
                        await m.delete()
                        return await message.reply("Oops, something went wrong!")
                try:
                    dump_file = await message.reply_video(content_value, caption="Thank you for using our bot!")
                except:
                    downfile = f"{os.getcwd()}/{random.randint(1, 10000000)}.mp4"
                    with open(downfile, 'wb') as x:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                        x.write(requests.get(content_value, headers=headers).content)
                    dump_file = await message.reply_video(downfile, caption="Thank you for using our bot!")
                    os.remove(downfile)
            elif "/p/" in link:
                meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
                if meta_tag.ok:
                    res = meta_tag.json()
                    meta = re.findall(r'href="(https?://[^"]+)"', res['data'])
                    for i in range(len(meta) - 1):
                        com = await message.reply_text(meta[i])
                        await asyncio.sleep(1)
                        try:
                            dump_file = await message.reply_video(com.text, caption="Thank you for using our bot!")
                            await com.delete()
                        except:
                            pass
                else:
                    await m.delete()
                    return await message.reply("Oops, something went wrong!")
            elif "stories" in link:
                meta_tag = requests.post("https://saveig.app/api/ajaxSearch", data={"q": link, "t": "media", "lang": "en"}, headers=headers)
                if meta_tag.ok:
                    res = meta_tag.json()
                    meta = re.findall(r'href="(https?://[^"]+)"', res['data'])
                    try:
                        dump_file = await message.reply_video(meta[0], caption="Thank you for using our bot!")
                    except:
                        com = await message.reply(meta[0])
                        await asyncio.sleep(1)
                        try:
                            dump_file = await message.reply_video(com.text, caption="Thank you for using our bot!")
                            await com.delete()
                        except:
                            pass
                else:
                    await m.delete()
                    return await message.reply("Oops, something went wrong!")
        except KeyError:
            await m.delete()
            await message.reply("Sorry, unable to find it. Make sure it's publicly available!")
        except Exception:
            await m.delete()
            await message.reply("Sorry, unable to find it. Try another link or report to support!")

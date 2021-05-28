import traceback
from asyncio import gather
from os import remove
from random import randint

from pykeyboard import InlineKeyboard
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton

from wbb import app, arq
from wbb.core.decorators.errors import capture_err
from wbb.utils.formatter import convert_seconds_to_minutes as timeFormat
from wbb.utils.functions import downloader

__MODULE__ = "YoutubeDL"
__HELP__ = "/ytdl [VIDEO_LINK] - Download a youtube video."


VIDEO_DATA = {}


@app.on_message(filters.command("ytdl"))
async def ytdl_func(_, message):
    if len(message.command) != 2:
        await message.reply_text("**Usage:**/ytdl [VIDEO_LINK]")
        return
    m = await message.reply_text("Processing")
    url = message.text.split(None, 1)[1]
    results = await arq.ytdl(url)
    if not results.ok:
        await message.reply_text(results.result)
        return
    result = results.result
    title = result.title
    thumbnail = result.thumbnail
    duration = result.duration
    video = result.video
    buttons = InlineKeyboard(row_width=3)
    keyboard = []
    for media in video:
        quality = media.quality
        size = media.size
        url = media.url
        format = media.format
        data = str(randint(999, 9999999))
        VIDEO_DATA[data] = {
            "url": url,
            "title": title,
            "size": size,
            "quality": quality,
            "duration": duration,
            "format": format,
            "thumbnail": thumbnail,
        }
        keyboard.append(
            InlineKeyboardButton(
                text=f"{quality} | {size}", callback_data=f"ytdl {data}"
            )
        )
    buttons.add(*keyboard)
    caption = f"""
**Title:** {title}
**Duration:** {await timeFormat(duration)}
**Size:** {size}
"""
    await message.reply_photo(thumbnail, caption=caption, reply_markup=buttons)
    await m.delete()


@app.on_callback_query(filters.regex(r"^ytdl"))
async def ytdlCallback(_, cq):
    await cq.message.edit("Downloading")
    data_ = cq.data.split()[1]
    try:
        data = VIDEO_DATA[data_]
        url = data["url"]
        title = data["title"]
        duration = data["duration"]
        format = data["format"]
        size = data["size"]
        thumbnail = data["thumbnail"]
        caption = f"""
**Title:** {title}
**Size:** {size}
**Format:** {format}
**Duration:** {await timeFormat(duration)}
        """
        media, thumb = await gather(
            downloader.download(url), downloader.download(thumbnail)
        )
        await cq.message.edit("Uploading")
        if format == "mp3":
            await cq.message.reply_audio(
                media,
                quote=False,
                caption=caption,
                duration=duration,
                thumb=thumb,
                title=title,
            )
        else:
            await cq.message.reply_video(
                media,
                caption=caption,
                quote=False,
                duration=duration,
                supports_streaming=True,
            )
        del VIDEO_DATA[data_]
        remove(thumb)
        remove(media)
        await cq.message.delete()
    except Exception as e:
        e = traceback.format_exc()
        print(e)
        del VIDEO_DATA[data_]
        await cq.message.delete()

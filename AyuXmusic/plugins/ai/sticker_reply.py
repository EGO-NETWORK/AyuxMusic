import os
import random
import time

from pyrogram import filters
from AyuXmusic import app

PACKS = [
    "tmedancestickrrpack_by_fStikBot_by_fStikBot",
    "http_MyStickershwuw_by_fStikBot",
    "EGOxQUOTES",
    "lovestickerrrr_by_fStikBot_by_fStikBot",
]

for item in os.getenv("AYU_EXTRA_STICKER_PACKS", "").split(","):
    item = item.strip()
    if item:
        PACKS.append(item)

CACHE = []
LAST = {}

CHANCE = int(os.getenv("AYU_STICKER_GROUP_CHANCE", "35") or 35)
COOLDOWN = int(os.getenv("AYU_STICKER_COOLDOWN", "25") or 25)


def private_chat(message):
    return "private" in str(message.chat.type).lower()


def can_reply(chat_id):
    now = time.time()
    if now - LAST.get(chat_id, 0) < COOLDOWN:
        return False
    LAST[chat_id] = now
    return True


async def load_stickers(client):
    if CACHE:
        return CACHE

    for pack in PACKS:
        try:
            sticker_set = await client.get_sticker_set(pack)
            for sticker in sticker_set.stickers:
                if sticker.file_id:
                    CACHE.append(sticker.file_id)
        except Exception:
            pass

    return CACHE


@app.on_message(filters.sticker & ~filters.bot)
async def ayu_sticker_reply(client, message):
    if not private_chat(message):
        if not can_reply(message.chat.id):
            return
        if random.randint(1, 100) > CHANCE:
            return

    stickers = await load_stickers(client)
    if stickers:
        await message.reply_sticker(random.choice(stickers))
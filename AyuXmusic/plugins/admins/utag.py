import asyncio
import html
import random
from contextlib import suppress

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from AyuXmusic import app
from AyuXmusic.misc import SUDOERS
from config import BANNED_USERS

UTAG_TASKS = {}
UTAG_DELAY = 1.8

UTAG_LINES = [
    "🥂 𝐇ᴇʏ 𝐁ʙᴜ 🤍 𝐓ᴜᴍʜᴀʀᴀ 𝐑ᴇᴘʟʏ 𝐈ᴛɴᴀ 𝐑ᴀʀᴇ 𝐇ᴀɪ 𝐊ɪ 𝐒ᴄʀᴇᴇɴꜱʜᴏᴛ 𝐋ᴇᴋᴇ 𝐅ʀᴀᴍᴇ 𝐊ᴀʀɴᴇ 𝐊ᴀ 𝐌ᴀɴɴ 𝐊ᴀʀᴛᴀ 𝐇ᴀɪ ✨",
    "🥂 𝐎ʏᴇ 𝐉ᴀɴᴜ 🌙 𝐂ʜᴀᴛ 𝐎ᴘᴇɴ 𝐊ᴀʀᴋᴇ 𝐒ɪʀꜰ 𝐑ᴇᴀᴅ 𝐊ᴀʀɴᴀ 𝐈ʟʟᴇɢᴀʟ 𝐇ᴏɴᴀ 𝐂ʜᴀʜɪʏᴇ 😭",
    "🥂 𝐇ᴇʟʟᴏ 𝐂ᴜᴛɪᴇ 🖤 𝐓ᴜᴍ 𝐎ɴʟɪɴᴇ 𝐀ᴀᴛᴇ 𝐇ᴏ 𝐓ᴏ 𝐋ᴀɢᴛᴀ 𝐇ᴀɪ 𝐀ʙ 𝐕ɪʙᴇ 𝐀ᴀʏᴇɢɪ… 𝐏ʜɪʀ 𝐓ᴜᴍ 𝐂ʜᴀʟᴇ 𝐉ᴀᴛᴇ 𝐇ᴏ ✨",
    "🥂 𝐒ᴜɴᴏ 𝐁ʙʏ 💌 𝐓ʜᴏᴅᴀ ꜱᴀ 𝐓ɪᴍᴇ 𝐂ʜᴀᴛ 𝐊ᴏ 𝐁ʜɪ 𝐃ᴇ 𝐃ɪʏᴀ 𝐊ᴀʀᴏ, 𝐒ᴀʙᴋᴏ 𝐓ᴜᴍʜᴀʀɪ 𝐄ɴᴇʀɢʏ 𝐏ᴀꜱᴀɴᴅ 𝐇ᴀɪ 🌸",
    "🥂 𝐇ᴇʏ 𝐏ᴏᴏᴋɪᴇ ✨ 𝐈ᴛɴᴀ 𝐋ᴀᴛᴇ 𝐑ᴇᴘʟʏ 𝐊ᴀʀᴛᴇ 𝐇ᴏ 𝐊ɪ 𝐓ᴀʙ 𝐓ᴀᴋ 𝐓ᴏᴘɪᴄ 𝐇ɪ 𝐂ʜᴀɴɢᴇ 𝐇ᴏ 𝐉ᴀᴛᴀ 𝐇ᴀɪ 😭",
    "🥂 𝐎ʏᴇ 𝐁ᴜʙᴜ 🌸 𝐓ᴜᴍʜᴀʀᴇ “𝐇ᴍᴍᴍ” 𝐌ᴇ 𝐁ʜɪ 𝐋ᴏɢ 𝐌ᴇᴀɴɪɴɢ 𝐃ʜᴜɴᴅʜɴᴇ 𝐋ᴀɢᴛᴇ 𝐇ᴀɪ ✨",
    "🥂 𝐇ᴇʟʟᴏ 𝐉ᴀᴀɴ 🤍 𝐂ʜᴀᴛ 𝐌ᴇ 𝐓ᴜᴍʜᴀʀᴀ 𝐍ᴀᴍᴇ 𝐃ɪᴋʜ 𝐉ᴀʏᴇ 𝐓ᴏ 𝐌ᴏᴏᴅ 𝐓ʜᴏᴅᴀ 𝐁ᴇᴛᴛᴇʀ 𝐇ᴏ 𝐉ᴀᴛᴀ 𝐇ᴀɪ 🌙",
    "🥂 𝐇ᴇʏ 𝐀ɴɢᴇʟ 🌙 𝐓ᴜᴍ 𝐈ᴛɴᴇ 𝐒ɪʟᴇɴᴛ 𝐊ʏᴜ 𝐑ᴇʜᴛᴇ 𝐇ᴏ? 𝐆𝐂 𝐊ᴏ 𝐁ʜɪ 𝐓ʜᴏᴅᴀ 𝐀ᴛᴛᴇɴᴛɪᴏɴ 𝐂ʜᴀʜɪʏᴇ ✨",
    "🥂 𝐎ʏᴇ 𝐁ʙʏ 🖤 𝐀ᴀᴘᴋɪ 𝐏𝐅𝐏 𝐀ᴄʜɪ 𝐍ʜɪ 𝐇 😭 @PFPEMPIRE 𝐘ᴀʜᴀ ꜱᴇ 𝐄ᴋ 𝐀ᴇꜱᴛʜᴇᴛɪᴄ 𝐏𝐅𝐏 𝐋ᴇʟᴏ ✨",
    "🥂 𝐒ᴜɴᴏ 𝐂ᴜᴛɪᴇ 💫 𝐏𝐅𝐏 𝐂ʜᴀɴɢᴇ 𝐊ᴀʀɴᴇ 𝐊ᴀ 𝐌ᴏᴏᴅ 𝐇ᴏ 𝐓ᴏ @PFPEMPIRE 𝐘ᴀʜᴀ ꜱᴇ 𝐋ᴇʟᴇɴᴀ 🌸",
    "🥂 𝐎ʏᴇ 𝐒ᴛᴀʀ 🌟 𝐓ᴜᴍʜᴀʀɪ 𝐄ɴᴛʀʏ 𝐇ᴏ 𝐉ᴀʏᴇ 𝐓ᴏ 𝐂ʜᴀᴛ 𝐊ᴀ 𝐌ᴏᴏᴅ 𝐀ᴜᴛᴏ 𝐔ᴘɢʀᴀᴅᴇ 𝐇ᴏ 𝐉ᴀᴛᴀ 𝐇ᴀɪ",
    "🥂 𝐇ᴇʏ 𝐂ʜᴀʀᴍᴇʀ 💫 𝐓ᴜᴍ 𝐎ɴʟɪɴᴇ 𝐀ᴀᴏ 𝐓ᴏ 𝐆𝐂 𝐊ᴏ 𝐓ʜᴏᴅᴀ 𝐒ᴀ 𝐌ᴀɢɪᴄ 𝐌ɪʟ 𝐉ᴀᴛᴀ 𝐇ᴀɪ",
    "🥂 𝐒ᴜɴᴏ 𝐏ʏᴀʀᴇ 🤍 𝐂ʜᴀᴛ 𝐌ᴇ 𝐓ᴜᴍʜᴀʀᴀ 𝐑ᴇᴘʟʏ 𝐀ᴀʏᴇ 𝐓ᴏ 𝐃ᴀʏ 𝐁ᴇᴛᴛᴇʀ 𝐋ᴀɢɴᴇ 𝐋ᴀɢᴛᴀ 𝐇ᴀɪ",
    "🥂 𝐎ʏᴇ 𝐂ᴜᴛᴇ 𝐒ᴏᴜʟ 🌙 𝐈ᴛɴᴀ 𝐌ᴀᴛ 𝐂ʜᴜᴘ 𝐑ᴀʜᴏ, 𝐓ᴜᴍʜᴀʀɪ 𝐕ɪʙᴇ 𝐒ᴀʙᴋᴏ 𝐌ɪꜱꜱ 𝐇ᴏ 𝐑ᴀʜɪ 𝐇ᴀɪ",
    "🥂 𝐇ᴇʏ 𝐁ᴇꜱᴛɪᴇ ✨ 𝐓ᴜᴍʜᴀʀᴀ 𝐎ɴᴇ 𝐌ᴇꜱꜱᴀɢᴇ 𝐁ʜɪ 𝐆𝐂 𝐊ᴀ 𝐓ʀᴀꜰꜰɪᴄ 𝐁ᴀᴅʜᴀ 𝐃ᴇᴛᴀ 𝐇ᴀɪ",
    "🥂 𝐉ᴀᴀɴ 💌 𝐓ᴜᴍʜᴀʀᴀ 𝐑ᴇᴘʟʏ 𝐋ᴀᴛᴇ 𝐇ᴏ 𝐒ᴀᴋᴛᴀ 𝐇ᴀɪ, 𝐏ᴀʀ 𝐕ᴀʟᴜᴇ 𝐀ʟᴡᴀʏꜱ 𝐇ɪɢʜ 𝐇ᴏᴛɪ 𝐇ᴀɪ",
    "🥂 𝐇ᴇʟʟᴏ 𝐒ᴡᴇᴇᴛʏ 🌸 𝐓ᴜᴍ 𝐂ʜᴀᴛ 𝐌ᴇ 𝐀ᴀᴏ 𝐓ᴏ 𝐒ᴀʙᴋᴏ 𝐓ʜᴏᴅᴀ 𝐒ᴀ 𝐒ᴍɪʟᴇ 𝐌ɪʟ 𝐉ᴀᴛᴀ 𝐇ᴀɪ",
    "🥂 𝐎ʏᴇ 𝐌ᴏᴏɴʟɪɢʜᴛ 🌙 𝐒ɪʟᴇɴᴛ 𝐌ᴏᴅᴇ 𝐎ꜰꜰ 𝐊ᴀʀᴏ, 𝐆𝐂 𝐓ᴜᴍʜᴇ 𝐌ɪꜱꜱ 𝐊ᴀʀ 𝐑ᴀʜᴀ 𝐇ᴀɪ",
    "🥂 𝐄xᴄᴜꜱᴇ 𝐌ᴇ 𝐉ɪ 💌 𝐀ᴀᴘᴋᴀ 𝐀ᴄᴛɪᴠᴇ 𝐕ᴇʀꜱɪᴏɴ 𝐊ᴀʙ 𝐑ᴇʟᴇᴀꜱᴇ 𝐇ᴏɢᴀ? ✨",
    "🥂 𝐎ʏᴇ 𝐂ᴜᴛɪᴇ ✨ 𝐓ᴜᴍʜᴀʀᴀ “𝐇ɪ” 𝐁ʜɪ 𝐏ᴜʀᴇ 𝐂ʜᴀᴛ 𝐊ᴀ 𝐕ɪʙᴇ 𝐂ʜᴀɴɢᴇ 𝐊ᴀʀ 𝐃ᴇᴛᴀ 𝐇ᴀɪ 🌙",
    "🥂 𝐒ᴜɴᴏ 𝐉ᴀᴀɴ 🌸 𝐈ᴛɴᴀ 𝐀ᴛᴛɪᴛᴜᴅᴇ 𝐀ᴄʜᴀ 𝐍ᴀʜɪ 𝐇ᴏᴛᴀ, 𝐊ᴀʙʜɪ 𝐓ᴏ 𝐅ɪʀꜱᴛ 𝐌ᴇꜱꜱᴀɢᴇ 𝐊ᴀʀ 𝐃ɪʏᴀ 𝐊ᴀʀᴏ ✨",
    "🥂 𝐇ᴇʏ 𝐁ʙᴜ 🖤 𝐈ꜰ 𝐘ᴏᴜ 𝐍ᴇᴇᴅ 𝐏ʀᴇᴍɪᴜᴍ 𝐎ʀ 𝐓𝐆 𝐈𝐃ꜱ, 𝐉ᴜꜱᴛ 𝐃ᴍ @EGOISTICXPRIME✨",
    "🥂 𝐎ʏᴇ 𝐉ᴀᴀɴ 💌 𝐓𝐆 𝐈𝐃 𝐁ᴜʏ 𝐊ᴀʀɴɪ 𝐇ᴏ 𝐓ᴏ @EGOISTICXPRIME 𝐊ᴏ 𝐃ᴍ 𝐊ᴀʀ 𝐋ᴏ 🌙",
    "🥂 𝐇ᴇʏ 𝐌ᴏᴏɴʟɪɢʜᴛ 🌙 𝐀ᴀᴊ 𝐓ʜᴏᴅᴀ 𝐓ᴜᴍ 𝐁ʜɪ 𝐂ʜᴀᴛ 𝐌ᴇ 𝐂ʜᴀᴍᴀᴋ 𝐉ᴀᴏ ✨",
    "🥂 𝐇ᴇʟʟᴏ 𝐁ʙʏ 🌙 𝐀ᴀᴊ 𝐊ᴀ 𝐓ᴀꜱᴋ: 𝐆ʜᴏꜱᴛ 𝐌ᴏᴅᴇ 𝐎ꜰꜰ 𝐊ᴀʀᴋᴇ 𝐄ᴋ 𝐏ʏᴀʀᴀ ꜱᴀ 𝐑ᴇᴘʟʏ 𝐃ᴇɴᴀ 😭",
]


def _format_user_mention(user) -> str:
    name = html.escape(user.first_name or user.username or "User")
    return f'<a href="tg://user?id={user.id}">{name}</a>'


async def _is_group_admin(message: Message) -> bool:
    if not message.from_user:
        return False
    if message.from_user.id in SUDOERS:
        return True
    try:
        member = await app.get_chat_member(message.chat.id, message.from_user.id)
    except Exception:
        return False
    return member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)


async def _send_utag_message(chat_id: int, mention: str, reply_id: int):
    line = html.escape(random.choice(UTAG_LINES))
    text = f"{mention}\n\n{line}"
    while True:
        try:
            return await app.send_message(
                chat_id,
                text,
                disable_web_page_preview=True,
                reply_to_message_id=reply_id,
            )
        except FloodWait as fw:
            if fw.value > 300:
                raise
            await asyncio.sleep(fw.value)


async def _run_utag(chat_id: int, status: Message, reply_id: int):
    total = 0
    try:
        async for member in app.get_chat_members(chat_id):
            user = member.user
            if not user or user.is_bot or getattr(user, "is_deleted", False):
                continue

            await _send_utag_message(chat_id, _format_user_mention(user), reply_id)
            total += 1
            await asyncio.sleep(UTAG_DELAY)

        if total:
            await status.edit_text(f"Utag completed. Tagged {total} members.")
        else:
            await status.edit_text("No members found to tag.")
    except asyncio.CancelledError:
        with suppress(Exception):
            await status.edit_text(f"Utag stopped. Tagged {total} members.")
        raise
    except FloodWait as fw:
        await status.edit_text(f"Utag stopped by Telegram floodwait. Try again after {fw.value} seconds.")
    except Exception as exc:
        await status.edit_text(f"Failed to utag members: <code>{html.escape(type(exc).__name__)}</code>")
    finally:
        UTAG_TASKS.pop(chat_id, None)


@app.on_message(filters.command(["utag"]) & filters.group & ~BANNED_USERS)
async def utag_members(client, message: Message):
    if message.sender_chat:
        return await message.reply_text("Use /utag from your user account, not anonymous admin mode.")
    if not await _is_group_admin(message):
        return await message.reply_text("Only group admins and owner can use /utag.")
    if message.chat.id in UTAG_TASKS:
        return await message.reply_text("Utag is already running in this group. Use /ustop to cancel it.")

    status = await message.reply_text("Utag started. Use /ustop to cancel.")
    task = asyncio.create_task(_run_utag(message.chat.id, status, message.id))
    UTAG_TASKS[message.chat.id] = task


@app.on_message(filters.command(["ustop"]) & filters.group & ~BANNED_USERS)
async def stop_utag(client, message: Message):
    if message.sender_chat:
        return await message.reply_text("Use /ustop from your user account, not anonymous admin mode.")
    if not await _is_group_admin(message):
        return await message.reply_text("Only group admins and owner can stop utag.")

    task = UTAG_TASKS.get(message.chat.id)
    if not task:
        return await message.reply_text("No utag is running in this group.")

    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
    await message.reply_text("Utag stopped.")

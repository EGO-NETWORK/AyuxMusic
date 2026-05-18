import asyncio
import html
from contextlib import suppress

from pyrogram import StopPropagation, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from AyuXmusic import app
from AyuXmusic.misc import SUDOERS
from config import BANNED_USERS

TAGALL_TASKS = {}
MENTIONS_PER_MESSAGE = 5
TAG_DELAY = 1.5
MAX_HEADER_LENGTH = 2800


def _format_user_mention(user) -> str:
    name = html.escape(user.first_name or user.username or "User")
    return f'<a href="tg://user?id={user.id}">{name}</a>'


def _get_tag_text(message: Message) -> str | None:
    if len(message.command) > 1:
        raw_text = message.text or message.caption or ""
        return raw_text.split(None, 1)[1].strip()
    if message.reply_to_message:
        replied = message.reply_to_message
        return (replied.text or replied.caption or "").strip() or None
    return None


def _trim_header(text: str | None) -> str | None:
    if not text:
        return None
    text = html.escape(text.strip())
    if len(text) <= MAX_HEADER_LENGTH:
        return text
    return text[:MAX_HEADER_LENGTH].rstrip() + "..."


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


async def _send_tag_batch(chat_id: int, mentions: list[str], header: str | None, reply_id: int | None):
    text = " ".join(mentions)
    if header:
        text = f"{header}\n\n{text}"
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


async def _run_tagall(chat_id: int, status: Message, header: str | None, reply_id: int | None):
    total = 0
    batch = []
    first_batch = True
    try:
        async for member in app.get_chat_members(chat_id):
            user = member.user
            if not user or user.is_bot or getattr(user, "is_deleted", False):
                continue

            batch.append(_format_user_mention(user))
            if len(batch) < MENTIONS_PER_MESSAGE:
                continue

            await _send_tag_batch(chat_id, batch, header if first_batch else None, reply_id)
            total += len(batch)
            batch.clear()
            first_batch = False
            await asyncio.sleep(TAG_DELAY)

        if batch:
            await _send_tag_batch(chat_id, batch, header if first_batch else None, reply_id)
            total += len(batch)

        if total:
            await status.edit_text(f"Tagall completed. Tagged {total} members.")
        else:
            await status.edit_text("No members found to tag.")
    except asyncio.CancelledError:
        with suppress(Exception):
            await status.edit_text(f"Tagall stopped. Tagged {total} members.")
        raise
    except FloodWait as fw:
        await status.edit_text(f"Tagall stopped by Telegram floodwait. Try again after {fw.value} seconds.")
    except Exception as exc:
        await status.edit_text(f"Failed to tag members: <code>{html.escape(type(exc).__name__)}</code>")
    finally:
        TAGALL_TASKS.pop(chat_id, None)


@app.on_message(filters.command(["tagall"]) & filters.group & ~BANNED_USERS)
async def tag_all_members(client, message: Message):
    if message.sender_chat:
        return await message.reply_text("Use /tagall from your user account, not anonymous admin mode.")
    if not await _is_group_admin(message):
        return await message.reply_text("Only group admins and owner can use /tagall.")
    if message.chat.id in TAGALL_TASKS:
        return await message.reply_text("Tagall is already running in this group. Use /stop to cancel it.")

    tag_text = _trim_header(_get_tag_text(message))
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    if not tag_text and not message.reply_to_message:
        return await message.reply_text(
            "Usage:\n/tagall <message>\nOr reply /tagall to any message."
        )

    status = await message.reply_text("Tagall started. Use /stop to cancel.")
    task = asyncio.create_task(_run_tagall(message.chat.id, status, tag_text, reply_id))
    TAGALL_TASKS[message.chat.id] = task


@app.on_message(filters.command(["stop"]) & filters.group & ~BANNED_USERS, group=-2)
async def stop_tagall(client, message: Message):
    if message.sender_chat:
        await message.reply_text("Use /stop from your user account, not anonymous admin mode.")
        raise StopPropagation
    if not await _is_group_admin(message):
        await message.reply_text("Only group admins and owner can stop tagall.")
        raise StopPropagation

    task = TAGALL_TASKS.get(message.chat.id)
    if not task:
        await message.reply_text("No tagall is running in this group.")
        raise StopPropagation

    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
    await message.reply_text("Tagall stopped.")
    raise StopPropagation

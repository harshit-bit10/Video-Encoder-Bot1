# VideoEncoder - a telegram bot for compressing/encoding videos in h264/h265 format.
# Copyright (c) 2021 WeebTime/VideoEncoder
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import shutil
import time
from os import execl as osexecl
from subprocess import run as srun
from sys import executable
from time import time

from psutil import (boot_time, cpu_count, cpu_percent, disk_usage,
                    net_io_counters, swap_memory, virtual_memory)
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, InviteLinkExpired

from .. import botStartTime, download_dir, encode_dir
from ..utils.database.access_db import db
from ..utils.database.add_user import AddUserToDatabase
from ..utils.display_progress import TimeFormatter, humanbytes
from ..utils.helper import check_chat, start_but

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


def uptime():
    """ returns uptime """
    return TimeFormatter(time.time() - botStartTime)


@Client.on_message(filters.command('start'))
async def start_message(app, message):
    c = await check_chat(message, chat='Both')
    if not c:
        return
    await AddUserToDatabase(app, message)
    text = f"Hi {message.from_user.mention()}<a href='https://telegra.ph/shvb1-01-27'>!</a> I'm VideoEncoder Bot which will do magic with your file.\n<b>Made with Love By @SupremeYoriichi</b>"
    await message.reply(text=text, reply_markup=start_but)


@Client.on_message(filters.command('help'))
async def help_message(app, message):
    c = await check_chat(message, chat='Both')
    if not c:
        return
    await AddUserToDatabase(app, message)
    msg = """<b>📕 Commands List</b>:

- Autodetect Telegram File.
- /ddl - encode through DDL
- /batch - encode in batch
- /about - about our bot 
- /queue - check queue
- /settings - settings
- /vset - view settings
- /reset - reset settings
- /stats - cpu stats

For Sudo:
- /exec - Execute Python
- /sh - Execute Shell
- /vupload - video upload
- /dupload - doc upload
- /gupload - drive upload
- /update - git pull
- /restart - restart bot
- /clean - clean junk
- /clear - clean queue
- /logs - view logs

For Owner:
- /addchat and /addsudo
- /rmsudo and /rmchat

Supports: <a href='https://telegra.ph/SharkToonsIndia-Video---Encoder-Bot-Supports-01-28'>click here</a>"""
    await message.reply(text=msg, disable_web_page_preview=True, reply_markup=start_but)

@app.on_message(filters.command("about"))
async def about(client, message):
    # Send the image first
    await client.send_photo(
        chat_id=message.chat.id,
        photo="https://telegra.ph/file/your_image_file_id_or_url.jpg",  # Replace with your image URL
        caption=(
            "<b><i>About Us..\n\n"
            "For more information, visit: https://telegra.ph/Shvb2-01-27\n\n"
            "‣ Made for : V-1 {t.me/@SharkToonsIndia} And V-2 {t.me/@SharkToonsBackup}\n"
            "‣ Owned by : @SupremeYoriichi\n"
            "‣ Maintained by : @SupremeYoriichi\n"
            "‣ Developed by : Team WZ\n\n"
            "That's It !! </i></b>"
        )
    )

@Client.on_message(filters.command('stats'))
async def show_status_count(_, event: Message):
    c = await check_chat(event, chat='Both')
    if not c:
        return
    await AddUserToDatabase(_, event)
    text = await show_status(_)
    await event.reply_text(text)


async def show_status(_):
    currentTime = TimeFormatter(time() - botStartTime)
    osUptime = TimeFormatter(time() - boot_time())
    total, used, free, disk = disk_usage('/')
    total = humanbytes(total)
    used = humanbytes(used)
    free = humanbytes(free)
    sent = humanbytes(net_io_counters().bytes_sent)
    recv = humanbytes(net_io_counters().bytes_recv)
    cpuUsage = cpu_percent(interval=0.5)
    p_core = cpu_count(logical=False)
    t_core = cpu_count(logical=True)
    swap = swap_memory()
    swap_p = swap.percent
    memory = virtual_memory()
    mem_t = humanbytes(memory.total)
    mem_a = humanbytes(memory.available)
    mem_u = humanbytes(memory.used)
    total_users = await db.total_users_count()
    text = f"""<b>Uptime of</b>:
- <b>Bot:</b> {currentTime}
- <b>OS:</b> {osUptime}

<b>Disk</b>:
<b>- Total:</b> {total}
<b>- Used:</b> {used}
<b>- Free:</b> {free}

<b>UL:</b> {sent} | <b>DL:</b> {recv}
<b>CPU:</b> {cpuUsage}%

<b>Cores:</b>
<b>- Physical:</b> {p_core}
<b>- Total:</b> {t_core}
<b>- Used:</b> {swap_p}%

<b>RAM:</b> 
- <b>Total:</b> {mem_t}
- <b>Free:</b> {mem_a}
- <b>Used:</b> {mem_u}

Users: {total_users}"""
    return text


async def showw_status(_):
    currentTime = TimeFormatter(time() - botStartTime)
    total, used, free, disk = disk_usage('/')
    total = humanbytes(total)
    used = humanbytes(used)
    free = humanbytes(free)
    cpuUsage = cpu_percent(interval=0.5)
    total_users = await db.total_users_count()

    text = f"""Uptime of Bot: {currentTime}

Disk:
- Total: {total}
- Used: {used}
- Free: {free}
CPU: {cpuUsage}%

Users: {total_users}"""
    return text


@Client.on_message(filters.command('clean'))
async def delete_files(_, message):
    c = await check_chat(message, chat='Sudo')
    if not c:
        return
    delete_downloads()
    await message.reply_text('Deleted all junk files!')


def delete_downloads():
    dir = encode_dir
    dir2 = download_dir
    for files in os.listdir(dir):
        path = os.path.join(dir, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)
    for files in os.listdir(dir2):
        path = os.path.join(dir2, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)


@Client.on_message(filters.command('restart'))
async def font_message(app, message):
    c = await check_chat(message, chat='Sudo')
    if not c:
        return
    await AddUserToDatabase(app, message)
    reply = await message.reply_text('Restarting...')
    textx = f"Done Restart...✅"
    await reply.edit_text(textx)
    try:
        exit()
    finally:
        osexecl(executable, executable, "-m", "VideoEncoder")

# Replace with the Telegram User ID of the bot owner
OWNER_ID = 6066102279  # Replace this with your Telegram User ID

# Global variables to store channel IDs
channel_1 = None
channel_2 = None
invite_link_1 = None
invite_link_2 = None

# Initialize the bot
app = Client("force_subscribe_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Helper function to check if the user is the owner
def is_owner(user_id):
    return user_id == OWNER_ID

@app.on_message(filters.command("fsub1"))
async def set_fsub1(client, message):
    global channel_1, invite_link_1
    if not is_owner(message.from_user.id):
        await message.reply("🚫 You are not my master to access this command!")
        return

    if len(message.command) != 2:
        await message.reply("Usage: `/fsub1 -100{channel_id}`", parse_mode="markdown")
        return

    channel_1 = message.command[1]
    try:
        chat_member = await client.get_chat_member(channel_1, "me")
        if chat_member.status != "administrator":
            await message.reply("❌ Bot is not an admin in this channel. Please make the bot an admin and try again.")
            channel_1 = None
            return
        # Generate a new invite link
        invite_link_1 = await client.create_chat_invite_link(channel_1)
    except ChatAdminRequired:
        await message.reply("❌ Invalid Channel or Bot is not in the channel. Please check and try again.")
        channel_1 = None
        return

    await message.reply(f"✅ Channel 1 has been set to `{channel_1}`.")

@app.on_message(filters.command("fsub2"))
async def set_fsub2(client, message):
    global channel_2, invite_link_2
    if not is_owner(message.from_user.id):
        await message.reply("🚫 You are not my master to access this command!")
        return

    if len(message.command) != 2:
        await message.reply("Usage: `/fsub2 -100{channel_id}`", parse_mode="markdown")
        return

    channel_2 = message.command[1]
    try:
        chat_member = await client.get_chat_member(channel_2, "me")
        if chat_member.status != "administrator":
            await message.reply("❌ Bot is not an admin in this channel. Please make the bot an admin and try again.")
            channel_2 = None
            return
        # Generate a new invite link
        invite_link_2 = await client.create_chat_invite_link(channel_2)
    except ChatAdminRequired:
        await message.reply("❌ Invalid Channel or Bot is not in the channel. Please check and try again.")
        channel_2 = None
        return

    await message.reply(f"✅ Channel 2 has been set to `{channel_2}`.")

@app.on_message(filters.command("refresh_link"))
async def refresh_links(client, message):
    global invite_link_1, invite_link_2
    if not is_owner(message.from_user.id):
        await message.reply("🚫 You are not my master to access this command!")
        return

    if not channel_1 and not channel_2:
        await message.reply("❌ No channels are set yet. Please use `/fsub1` and `/fsub2` first.")
        return

    try:
        if channel_1:
            invite_link_1 = await client.create_chat_invite_link(channel_1)
        if channel_2:
            invite_link_2 = await client.create_chat_invite_link(channel_2)
        await message.reply("✅ Invite links have been refreshed successfully!")
    except InviteLinkExpired:
        await message.reply("❌ Failed to refresh invite links. Please check the channel settings.")

@app.on_message(filters.private)
async def force_subscribe(client, message):
    global channel_1, channel_2, invite_link_1, invite_link_2

    # Check if either channel_1 or channel_2 is set
    if not channel_1 and not channel_2:
        await message.reply("❌ Force subscription is not configured. Please contact the bot owner.")
        return

    # Inline buttons for channels
    buttons = []
    if channel_1:
        buttons.append([InlineKeyboardButton("Join Channel V1", url=invite_link_1.invite_link)])
    if channel_2:
        buttons.append([InlineKeyboardButton("Join Channel V2", url=invite_link_2.invite_link)])

    user_name = message.from_user.first_name or "User"
    user_profile = f"https://t.me/{message.from_user.username}" if message.from_user.username else f"https://t.me/{message.from_user.id}"

    try:
        # Check if user is a member of both channels
        if channel_1:
            await client.get_chat_member(channel_1, message.from_user.id)
        if channel_2:
            await client.get_chat_member(channel_2, message.from_user.id)
        # User is subscribed, allow access
        await message.reply("🎉 Welcome! You can now use the bot's features!\n<b>Bot By @SupremeYoriichi</b>")
    except UserNotParticipant:
        # User is not subscribed to one or more channels
        await message.reply_photo(
            "https://telegra.ph/Shinobuv3-01-28",  # Banner image
            caption=(
                f"Hey {user_name} [{user_profile}]\n\n"
                "Please Join Both Of Our Channels To Access Me And My Features."
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@Client.on_message(filters.command('update'))
async def update_message(app, message):
    c = await check_chat(message, chat='Sudo')
    if not c:
        return
    await AddUserToDatabase(app, message)
    reply = await message.reply_text('📶 Fetching Update...')
    textx = f"✅ Bot Updated"
    await reply.edit_text(textx)
    try:
        await app.stop()
    finally:
        srun([f"bash run.sh"], shell=True)

OWNER_ID = 6066102279  # Set as an integer

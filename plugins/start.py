#start.py
from pyrogram import Client, filters
from config import Config

@Client.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply("Halo! Selamat datang di bot Saweria.")

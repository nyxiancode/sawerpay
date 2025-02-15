#start.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config

@Client.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_photo(
        photo="https://example.com/logo.png",  # Ganti dengan URL logo
        caption="Selamat datang di bot Saweria!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Lihat Talent", callback_data="view_talents")]
        ])
    )

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import Database

db = Database()

@Client.on_message(filters.command("addtalent") & filters.user(Config.OWNER_ID))
async def add_talent(client, message):
    if message.reply_to_message and message.reply_to_message.photo:
        name = message.command[1]
        details = " ".join(message.command[2:])
        image_url = message.reply_to_message.photo.file_id
        db.save_talent(name, details, image_url)
        await message.reply(f"Talent {name} berhasil ditambahkan!")

@Client.on_message(filters.command("deltalent") & filters.user(Config.OWNER_ID))
async def del_talent(client, message):
    name = message.command[1]
    db.delete_talent(name)
    await message.reply(f"Talent {name} berhasil dihapus!")

@Client.on_message(filters.command("gettalent"))
async def get_talent(client, message):
    talents = db.get_all_talents()
    if talents:
        await message.reply("\n".join([t["name"] for t in talents]))
    else:
        await message.reply("Tidak ada talent terdaftar.")

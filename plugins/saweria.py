from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.saweria import Saweria
from database import Database

db = Database()
saweria = Saweria(user_id="your_saweria_user_id")

@Client.on_callback_query(filters.regex("^order_talent_"))
async def order_talent(client, callback_query):
    talent_name = callback_query.data.split("_")[2]
    talent = db.get_talent(talent_name)
    if talent:
        payment = saweria.create_payment(amount=10000, msg=f"Order {talent_name}")
        if payment["status"]:
            await callback_query.message.reply_photo(
                photo=payment["data"]["qr_image"],
                caption=f"Silakan scan QR code untuk membayar {talent_name}."
            )
            db.save_transaction(callback_query.from_user.id, talent_name, payment["data"]["id"])

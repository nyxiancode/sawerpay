import aiohttp
import io
import uuid
import qrcode
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import database
import config

# Dictionary untuk menyimpan data pembayaran yang sedang pending (simulasi)
pending_payments = {}

# Fungsi untuk mengambil status pembayaran dari Saweria (harus disesuaikan dengan logika scraping/endpoint yang sebenarnya)
async def get_payment_status(payment_id: str) -> dict:
    # Contoh endpoint; sesuaikan dengan endpoint atau scraping logic yang Anda buat
    url = f"https://saweria.com/api/check_payment?payid={payment_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data
            else:
                return {"status": "pending", "msg": "Pembayaran belum terdeteksi"}

# Inisialisasi Client Pyrogram
app = Client(
    "saweria_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# --------------------- COMMANDS --------------------- #

# /start: Menampilkan logo default dan tombol Talent
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    logo_url = database.get_logo() or "https://files.catbox.moe/0aojdt.jpg"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Talent", callback_data="talent_menu")]])
    caption = "Selamat datang di Bot Pembayaran Saweria!\nSilahkan pilih menu di bawah."
    await message.reply_photo(logo_url, caption=caption, reply_markup=keyboard)

# (Perintah /help, /setlogo, /addtalent, /deltalent, /gettalent, /setharga, /addvip, /setdeskripsi tetap sama seperti sebelumnya)
# ...

# --------------------- CALLBACK QUERIES --------------------- #

# Callback: Order Talent (Generate QR Code Pembayaran)
@app.on_callback_query(filters.regex("^order_"))
async def order_talent_callback(client, callback_query):
    data = callback_query.data  # Contoh: order_john
    talent_name = data.split("_", 1)[1]
    talent = database.get_talent(talent_name)
    if not talent:
        return await callback_query.answer("Talent tidak ditemukan.", show_alert=True)
    
    price = talent.get("price", 0)
    if price == 0:
        return await callback_query.answer("Harga belum diatur untuk talent ini.", show_alert=True)
    
    payment_id = str(uuid.uuid4())
    payment_url = f"https://saweria.com/payment?payid={payment_id}&amount={price}"
    
    # Generate QR Code menggunakan library qrcode
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(payment_url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    pending_payments[payment_id] = {
        "user_id": callback_query.from_user.id,
        "talent": talent_name,
        "price": price,
        "status": "pending"
    }
    
    # Tombol diubah menjadi "Cek Status Pembayaran"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Cek Status Pembayaran", callback_data=f"checkpay_{payment_id}")],
        [InlineKeyboardButton("Batal", callback_data="talent_menu")]
    ])
    caption = (
        f"Silahkan lakukan pembayaran untuk talent '{talent_name}'.\n"
        f"Harga: {price}\n\n"
        "Scan QR Code berikut dan setelah selesai, klik tombol 'Cek Status Pembayaran'."
    )
    await callback_query.message.reply_photo(photo=buf, caption=caption, reply_markup=keyboard)
    await callback_query.answer()

# Callback: Cek Status Pembayaran
@app.on_callback_query(filters.regex("^checkpay_"))
async def check_payment_callback(client, callback_query):
    data = callback_query.data  # Contoh: checkpay_<payment_id>
    payment_id = data.split("_", 1)[1]
    payment = pending_payments.get(payment_id)
    if not payment:
        return await callback_query.answer("Pembayaran tidak ditemukan.", show_alert=True)
    
    # Ambil status pembayaran dari Saweria secara langsung
    status_data = await get_payment_status(payment_id)
    
    if status_data.get("status") == "success":
        # Jika status sukses, catat transaksi dan hapus data pending
        database.record_transaction(payment["user_id"], payment["talent"], payment["price"], "success")
        pending_payments.pop(payment_id, None)
        
        talent = database.get_talent(payment["talent"])
        vip_channel = talent.get("vip_channel") if talent else None
        if vip_channel:
            invite_link = f"https://t.me/joinchat/dummyinvite_{payment_id}"
            invite_text = f"Berikut link VIP: {invite_link}"
        else:
            invite_text = "Link invite belum diset."
        
        thank_you_text = (
            f"Terima kasih, pembayaran Anda untuk talent '{payment['talent']}' sebesar {payment['price']} berhasil.\n\n"
            f"{invite_text}"
        )
        await client.send_message(callback_query.message.chat.id, thank_you_text)
        await callback_query.message.delete()
        await callback_query.answer("Pembayaran sukses!")
    else:
        # Jika belum sukses, beri notifikasi dengan pesan status
        await callback_query.answer(
            f"Pembayaran belum selesai. Status: {status_data.get('msg', 'pending')}",
            show_alert=True
        )

# Callback: Kembali ke Start (mengirim pesan baru dan menghapus pesan lama)
@app.on_callback_query(filters.regex("^back_to_start$"))
async def back_to_start_callback(client, callback_query):
    logo_url = database.get_logo() or "https://files.catbox.moe/0aojdt.jpg"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Talent", callback_data="talent_menu")]])
    caption = "Selamat datang di Bot Pembayaran Saweria!\nSilahkan pilih menu di bawah."
    await client.send_photo(
        chat_id=callback_query.message.chat.id,
        photo=logo_url,
        caption=caption,
        reply_markup=keyboard
    )
    await callback_query.message.delete()
    await callback_query.answer()

# Callback: Tampilkan Detail Talent (kirim pesan baru dan hapus pesan lama)
@app.on_callback_query(filters.regex("^talent_"))
async def talent_detail_callback(client, callback_query):
    data = callback_query.data  # Contoh: talent_john
    name = data.split("_", 1)[1]
    talent = database.get_talent(name)
    if not talent:
        return await callback_query.answer("Talent tidak ditemukan.", show_alert=True)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Kembali", callback_data="talent_menu")],
        [InlineKeyboardButton("Order Talent", callback_data=f"order_{talent['name']}")]
    ])
    caption = (
        f"Talent: {talent['name'].capitalize()}\n"
        f"Deskripsi: {talent['detail']}\n"
        f"Harga: {talent.get('price', 'Belum diatur')}"
    )
    await client.send_photo(
        chat_id=callback_query.message.chat.id,
        photo=talent["image_file_id"],
        caption=caption,
        reply_markup=keyboard
    )
    await callback_query.message.delete()
    await callback_query.answer()

# --------------------- RUN BOT --------------------- #

if __name__ == "__main__":
    print("Bot Saweria berjalan...")
    app.run()

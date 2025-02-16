import io
import uuid
import qrcode
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import database
import config

# Dictionary untuk menyimpan data pembayaran yang sedang pending (simulasi)
pending_payments = {}

# Inisialisasi Client Pyrogram
app = Client(
    "saweria_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# --------------------- COMMANDS --------------------- #

# /start: Menampilkan logo dan tombol Talent
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    logo_url = database.get_logo() or "https://files.catbox.moe/0aojdt.jpg"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Talent", callback_data="talent_menu")]])
    caption = "Selamat datang di Bot Pembayaran Saweria!\nSilahkan pilih menu di bawah."
    await message.reply_photo(logo_url, caption=caption, reply_markup=keyboard)

# /help: Menampilkan daftar perintah yang tersedia
@app.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    help_text = (
        "**Daftar Perintah yang Tersedia:**\n\n"
        "/start - Memulai bot dan menampilkan logo serta menu utama\n"
        "/help - Menampilkan daftar perintah\n"
        "/setlogo <url gambar> - Mengubah logo bot (hanya owner)\n"
        "/addtalent <url image> <nama talent> [detail] - Menambahkan talent dengan URL image dan nama (opsional detail, hanya owner)\n"
        "/deltalent <nama talent> - Menghapus talent (hanya owner)\n"
        "/gettalent - Menampilkan daftar talent (hanya owner)\n"
        "/setharga <nama talent> <harga> - Mengatur harga untuk talent (hanya owner)\n"
        "/addvip <nama talent> <id channel> - Menambahkan channel VIP untuk talent (hanya owner)\n"
    )
    await message.reply(help_text)

# /setlogo: Mengubah logo (hanya owner)
@app.on_message(filters.command("setlogo") & filters.private)
async def set_logo_command(client, message):
    if message.from_user.id != config.OWNER_ID:
        return
    if len(message.command) < 2:
        return await message.reply("Usage: /setlogo <url gambar>")
    logo_url = message.command[1]
    database.set_logo(logo_url)
    await message.reply("Logo berhasil diubah!")

# /addtalent: Menambahkan talent dengan format "/addtalent <url image> <nama talent> [detail]" (hanya owner)
@app.on_message(filters.command("addtalent") & filters.private)
async def add_talent_command(client, message):
    if message.from_user.id != config.OWNER_ID:
        return
    if len(message.command) < 3:
        return await message.reply("Usage: /addtalent <url image> <nama talent> [detail]")
    image_url = message.command[1]
    talent_name = message.command[2]
    detail = " ".join(message.command[3:]) if len(message.command) > 3 else ""
    database.add_talent(talent_name, detail, image_url)
    await message.reply(f"Talent '{talent_name}' berhasil ditambahkan.")

# /deltalent: Menghapus talent (hanya owner)
@app.on_message(filters.command("deltalent") & filters.private)
async def delete_talent_command(client, message):
    if message.from_user.id != config.OWNER_ID:
        return
    if len(message.command) < 2:
        return await message.reply("Usage: /deltalent <nama talent>")
    name = message.command[1]
    result = database.delete_talent(name)
    if result.deleted_count:
        await message.reply(f"Talent '{name}' berhasil dihapus.")
    else:
        await message.reply(f"Talent '{name}' tidak ditemukan.")

# /gettalent: Menampilkan daftar talent (hanya owner)
@app.on_message(filters.command("gettalent") & filters.private)
async def get_talent_command(client, message):
    if message.from_user.id != config.OWNER_ID:
        return
    talents = database.list_talents()
    if not talents:
        return await message.reply("Belum ada talent yang terdaftar.")
    text = "Daftar Talent:\n"
    for t in talents:
        text += f"- {t['name']} : {t['detail']}\n"
    await message.reply(text)

# /setharga: Mengatur harga talent (hanya owner)
@app.on_message(filters.command("setharga") & filters.private)
async def set_price_command(client, message):
    if message.from_user.id != config.OWNER_ID:
        return
    if len(message.command) < 3:
        return await message.reply("Usage: /setharga <nama talent> <harga>")
    name = message.command[1]
    try:
        price = float(message.command[2])
    except ValueError:
        return await message.reply("Harga harus berupa angka.")
    database.set_price(name, price)
    await message.reply(f"Harga untuk talent '{name}' berhasil diatur ke {price}.")

# /addvip: Menambahkan channel VIP untuk talent (hanya owner)
@app.on_message(filters.command("addvip") & filters.private)
async def add_vip_command(client, message):
    if message.from_user.id != config.OWNER_ID:
        return
    if len(message.command) < 3:
        return await message.reply("Usage: /addvip <nama talent> <id channel>")
    name = message.command[1]
    vip_channel = message.command[2]
    database.set_vip(name, vip_channel)
    await message.reply(f"Channel VIP untuk talent '{name}' berhasil ditambahkan: {vip_channel}")

# --------------------- CALLBACK QUERIES --------------------- #

# Callback: Tampilkan Menu Talent
@app.on_callback_query(filters.regex("^talent_menu$"))
async def talent_menu_callback(client, callback_query):
    talents = database.list_talents()
    if not talents:
        return await callback_query.answer("Belum ada talent yang tersedia.", show_alert=True)
    buttons = []
    for t in talents:
        buttons.append([InlineKeyboardButton(t["name"].capitalize(), callback_data=f"talent_{t['name']}")])
    buttons.append([InlineKeyboardButton("Kembali", callback_data="back_to_start")])
    await callback_query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
    await callback_query.answer()

# Callback: Kembali ke Start
@app.on_callback_query(filters.regex("^back_to_start$"))
async def back_to_start_callback(client, callback_query):
    logo_url = database.get_logo() or "https://example.com/default_logo.jpg"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Talent", callback_data="talent_menu")]])
    caption = "Selamat datang di Bot Pembayaran Saweria!\nSilahkan pilih menu di bawah."
    try:
        await callback_query.message.edit_media(
            media={"type": "photo", "media": logo_url, "caption": caption},
            reply_markup=keyboard
        )
    except Exception:
        await callback_query.message.reply_photo(logo_url, caption=caption, reply_markup=keyboard)
    await callback_query.answer()

# Callback: Tampilkan Detail Talent
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
        f"Detail: {talent['detail']}\n"
        f"Harga: {talent.get('price', 'Belum diatur')}"
    )
    try:
        await client.edit_message_media(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            media={"type": "photo", "media": talent["image_file_id"], "caption": caption},
            reply_markup=keyboard
        )
    except Exception as e:
        await callback_query.message.reply_text(f"Error: {e}")
    await callback_query.answer()

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
    
    # Buat payment ID unik
    payment_id = str(uuid.uuid4())
    # Simulasi URL pembayaran (di real case, gunakan automasi/scraping untuk mendapatkan QR Code dari Saweria)
    payment_url = f"https://saweria.com/payment?payid={payment_id}&amount={price}"
    
    # Generate QR Code menggunakan library qrcode
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(payment_url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    # Simpan data pembayaran pending (simulasi)
    pending_payments[payment_id] = {
        "user_id": callback_query.from_user.id,
        "talent": talent_name,
        "price": price,
        "status": "pending"
    }
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Saya Sudah Bayar", callback_data=f"checkpay_{payment_id}")],
        [InlineKeyboardButton("Batal", callback_data="talent_menu")]
    ])
    caption = (
        f"Silahkan lakukan pembayaran untuk talent '{talent_name}'.\n"
        f"Harga: {price}\n\n"
        "Scan QR Code berikut dan setelah selesai klik tombol 'Saya Sudah Bayar'."
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
    
    # Simulasi pengecekan pembayaran.
    payment["status"] = "success"
    
    # Catat transaksi ke database
    database.record_transaction(payment["user_id"], payment["talent"], payment["price"], "success")
    
    # Hapus data pembayaran pending
    pending_payments.pop(payment_id, None)
    
    # Jika talent memiliki channel VIP, simulasikan pembuatan link invite.
    talent = database.get_talent(payment["talent"])
    vip_channel = talent.get("vip_channel") if talent else None
    invite_text = "Link invite belum diset."
    if vip_channel:
        # Di real case, gunakan method export_chat_invite_link untuk membuat invite link baru.
        invite_link = f"https://t.me/joinchat/dummyinvite_{payment_id}"
        invite_text = f"Berikut link VIP: {invite_link}"
    
    thank_you_text = (
        f"Terima kasih, pembayaran Anda untuk talent '{payment['talent']}' sebesar {payment['price']} berhasil.\n\n"
        f"{invite_text}"
    )
    
    # Opsional: kirim notifikasi ke channel database jika diset
    settings = database.get_settings()
    if settings and settings.get("channel_database"):
        channel = settings.get("channel_database")
        try:
            await client.send_message(channel, thank_you_text)
        except Exception as e:
            print("Error mengirim ke channel:", e)
    
    await callback_query.message.edit_caption(caption=thank_you_text, reply_markup=None)
    await callback_query.answer("Pembayaran sukses!")

# --------------------- RUN BOT --------------------- #

if __name__ == "__main__":
    print("Bot Saweria berjalan...")
    app.run()

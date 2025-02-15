from pyrogram import Client
from plugins import start_handler, talent_handlers, saweria_handlers
from config import Config

app = Client(
    "saweria_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

app.run()

import os

class Config:
    API_ID = int(os.getenv("API_ID", 123456))  # Ganti dengan API ID Anda
    API_HASH = os.getenv("API_HASH", "your_api_hash")  # Ganti dengan API Hash Anda
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")  # Ganti dengan token bot Anda
    OWNER_ID = int(os.getenv("OWNER_ID", 123456789))  # Ganti dengan ID owner
    SAWERIA_EMAIL = os.getenv("SAWERIA_EMAIL", "your_email")  # Email Saweria
    SAWERIA_PASSWORD = os.getenv("SAWERIA_PASSWORD", "your_password")  # Password Saweria
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")  # MongoDB URI
    CHANNEL_DB = os.getenv("CHANNEL_DB", "your_channel_db")  # Channel untuk menyimpan log

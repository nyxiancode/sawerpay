from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URI)
# Menggunakan database default yang ditentukan dalam URI atau bisa disesuaikan nama databasenya
db = client.get_default_database()

def get_settings():
    return db.settings.find_one({})

def set_settings(data: dict):
    return db.settings.update_one({}, {"$set": data}, upsert=True)

def get_logo():
    settings = get_settings()
    if settings and "logo_url" in settings:
        return settings["logo_url"]
    return None

def set_logo(url: str):
    return set_settings({"logo_url": url})

def add_talent(name: str, detail: str, image_file_id: str, price: float = 0, vip_channel: str = None):
    talent = {
        "name": name.lower(),
        "detail": detail,
        "image_file_id": image_file_id,
        "price": price,
        "vip_channel": vip_channel
    }
    return db.talents.update_one({"name": name.lower()}, {"$set": talent}, upsert=True)

def delete_talent(name: str):
    return db.talents.delete_one({"name": name.lower()})

def get_talent(name: str):
    return db.talents.find_one({"name": name.lower()})

def list_talents():
    return list(db.talents.find())

def set_price(name: str, price: float):
    return db.talents.update_one({"name": name.lower()}, {"$set": {"price": price}})

def set_vip(name: str, vip_channel: str):
    return db.talents.update_one({"name": name.lower()}, {"$set": {"vip_channel": vip_channel}})

def record_transaction(user_id: int, talent_name: str, amount: float, status: str, invite_link: str = None):
    transaction = {
        "user_id": user_id,
        "talent": talent_name.lower(),
        "amount": amount,
        "status": status,
        "invite_link": invite_link
    }
    return db.transactions.insert_one(transaction)

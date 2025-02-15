from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client.saweria_bot

class Database:
    @staticmethod
    def save_talent(name, details, image_url):
        db.talents.update_one(
            {"name": name},
            {"$set": {"details": details, "image_url": image_url}},
            upsert=True
        )

    @staticmethod
    def get_talent(name):
        return db.talents.find_one({"name": name})

    @staticmethod
    def delete_talent(name):
        db.talents.delete_one({"name": name})

    @staticmethod
    def get_all_talents():
        return list(db.talents.find({}))

    @staticmethod
    def save_transaction(user_id, talent_name, payment_id):
        db.transactions.insert_one({
            "user_id": user_id,
            "talent_name": talent_name,
            "payment_id": payment_id,
            "status": "pending"
        })

    @staticmethod
    def update_transaction(payment_id, status):
        db.transactions.update_one(
            {"payment_id": payment_id},
            {"$set": {"status": status}}
        )

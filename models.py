from pymongo import MongoClient, ASCENDING
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
url_collection = db["urls"]
user_collection = db["users"]

# 🔥 Create Indexes (IMPORTANT for performance & uniqueness)
url_collection.create_index("short_id", unique=True)
user_collection.create_index("email", unique=True)


# =========================
# URL FUNCTIONS
# =========================

def create_url(data):
    return url_collection.insert_one(data)


def get_url(short_id):
    return url_collection.find_one({"short_id": short_id})


def increment_clicks(short_id):
    return url_collection.update_one(
        {"short_id": short_id},
        {"$inc": {"clicks": 1}}
    )


def get_urls_by_user(email):
    return list(url_collection.find({"user": email}))


# =========================
# USER FUNCTIONS
# =========================

def create_user(user):
    try:
        return user_collection.insert_one(user)
    except Exception:
        return None  # duplicate email case


def get_user_by_email(email):
    return user_collection.find_one({"email": email})
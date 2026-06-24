from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["notes_db"]

notes_collection = db["notes"]
users_collection = db["users"]
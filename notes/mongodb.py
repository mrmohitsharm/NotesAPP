from pymongo import MongoClient

client = MongoClient("mongodb+srv://mohitpurohit9636:mohitpurohit9636@cluster0.ssyldxq.mongodb.net/?appName=Cluster0")

db = client["notesdb"]

notes_collection = db["notes"]

users_collection = db["users"]
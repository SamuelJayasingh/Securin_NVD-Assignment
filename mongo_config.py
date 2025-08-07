import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_mongo_collection():
    username = os.getenv("MONGO_USERNAME")
    password = os.getenv("MONGO_PASSWORD")
    cluster = os.getenv("MONGO_CLUSTER")
    db_name = os.getenv("MONGO_DB")
    collection_name = os.getenv("MONGO_COLLECTION")

    if not all([username, password, cluster, db_name, collection_name]):
        raise ValueError("Missing MongoDB credentials or config in .env")

    uri = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority"
    client = MongoClient(uri)
    db = client[db_name]
    return db[collection_name]

import json
import time
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from mongo_config import get_mongo_collection
from fetch_utils import fetch_all_cves
from preprocess_utils import clean_and_deduplicate
from pymongo import UpdateOne

# Get MongoDB collection from config
collection = get_mongo_collection()

def upload_to_mongodb(cve_list):
    operations = [
        UpdateOne({"id": cve["id"]}, {"$set": cve}, upsert=True)
        for cve in cve_list
    ]
    if operations:
        result = collection.bulk_write(operations)
        print(f"Inserted: {result.upserted_count}, Updated: {result.modified_count}")
    else:
        print("No records to upload.")

# Fetches all CVEs, cleans them, and uploads to MongoDB
def full_sync():
    print("[Full Sync] Fetching all CVE records from NVD...")
    raw_data = fetch_all_cves()
    cleaned = clean_and_deduplicate(raw_data)
    upload_to_mongodb(cleaned)
    print(f"[Full Sync] Uploaded {len(cleaned)} records.")

# Fetches only modified CVEs in the last 24 hours
def incremental_sync():
    print("[Incremental Sync] Fetching CVEs modified in the last 24 hours...")
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    url_params = {
        "lastModStartDate": yesterday.isoformat() + "Z",
        "lastModEndDate": now.isoformat() + "Z"
    }

    raw_data = fetch_all_cves(url_params=url_params)
    cleaned = clean_and_deduplicate(raw_data)
    upload_to_mongodb(cleaned)
    print(f"[Incremental Sync] Uploaded {len(cleaned)} records.")

# Uploads data from local JSON file (already cleaned)
def upload_from_json(filepath="nvd_cleaned.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            cleaned_data = json.load(f)
            print(f"[JSON Upload] Loaded {len(cleaned_data)} records from {filepath}. Starting upload...")
            upload_to_mongodb(cleaned_data)
    except FileNotFoundError:
        print(f"File not found: {filepath}")

# Starts periodic sync jobs
def run_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(full_sync, 'cron', hour=1)
    scheduler.add_job(incremental_sync, 'interval', hours=2)
    scheduler.start()
    print("Scheduler is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("Scheduler stopped.")

if __name__ == "__main__":
    # Uncomment to run a full sync (downloads everything)
    # full_sync()

    # Upload from local JSON file
    upload_from_json()

    # Uncomment to enable periodic sync
    # run_scheduler()

    print("Finished.")

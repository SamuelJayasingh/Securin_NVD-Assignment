from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from firebase_config import init_firestore
from fetch_utils import fetch_all_cves
from preprocess_utils import clean_and_deduplicate
import time

db = init_firestore()

def upload_to_firestore(cve_list):
    for entry in cve_list:
        doc_id = entry["id"]
        db.collection("cves").document(doc_id).set(entry)
        print(f"Uploaded: {doc_id}")

def full_sync():
    print("[FULL SYNC] Starting full data fetch...")
    raw_data = fetch_all_cves()
    cleaned = clean_and_deduplicate(raw_data)
    upload_to_firestore(cleaned)
    print(f"[FULL SYNC] {len(cleaned)} records uploaded.\n")

def incremental_sync():
    print("[INCREMENTAL SYNC] Fetching updates from last 24 hours...")
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    url_params = {
        "lastModStartDate": yesterday.isoformat() + "Z",
        "lastModEndDate": now.isoformat() + "Z"
    }

    raw_data = fetch_all_cves(url_params=url_params)
    cleaned = clean_and_deduplicate(raw_data)
    upload_to_firestore(cleaned)
    print(f"[INCREMENTAL SYNC] {len(cleaned)} updated records uploaded.\n")

if __name__ == "__main__":
    full_sync() 
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(full_sync, 'cron', hour=1)               
    # scheduler.add_job(incremental_sync, 'interval', hours=2) #Syncs every 2 hours
    # scheduler.start()

    print("CVE Scheduler started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("Scheduler stopped.")

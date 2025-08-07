import requests
import time
from tqdm import tqdm

BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_cves(start_index=0, results_per_page=2000, url_params=None):
    params = {
        "startIndex": start_index,
        "resultsPerPage": results_per_page
    }
    if url_params:
        params.update(url_params)

    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def fetch_all_cves(limit=None, url_params=None):
    all_cves = []
    results_per_page = 2000
    start_index = 0

    first_batch = fetch_cves(start_index, results_per_page, url_params)
    if not first_batch:
        return []

    total = first_batch.get("totalResults", 0)
    if limit:
        total = min(limit, total)

    all_cves.extend(first_batch.get("vulnerabilities", []))
    start_index += results_per_page

    for i in tqdm(range(start_index, total, results_per_page), desc="Fetching CVEs"):
        time.sleep(1)
        batch = fetch_cves(i, results_per_page, url_params)
        if batch and "vulnerabilities" in batch:
            all_cves.extend(batch["vulnerabilities"])
        else:
            break

    return all_cves

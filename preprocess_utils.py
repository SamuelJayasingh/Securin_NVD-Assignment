import json
from datetime import datetime

def extract_description(descs):
    for d in descs:
        if d.get("lang") == "en":
            return d.get("value")
    return "No description"

def extract_score(metrics, version):
    try:
        key = f"cvssMetric{version}"
        return metrics[key][0]["cvssData"]["baseScore"]
    except:
        return None

def clean_and_deduplicate(raw_data):
    cleaned = []
    for item in raw_data:
        cve = item.get("cve", {})
        cve_id = cve.get("id")
        if not cve_id:
            continue

        try:
            year = datetime.fromisoformat(cve.get("published", "").replace("Z", "")).year
        except:
            year = None

        entry = {
            "id": cve_id,
            "published": cve.get("published"),
            "lastModified": cve.get("lastModified"),
            "description": extract_description(cve.get("descriptions", [])),
            "baseScoreV2": extract_score(cve.get("metrics", {}), "V2"),
            "baseScoreV3": extract_score(cve.get("metrics", {}), "V3"),
            "year": year,
            "sourceIdentifier": cve.get("sourceIdentifier"),
            "vulnStatus": cve.get("vulnStatus")
        }

        cleaned.append(entry)

    # Deduplicate by ID
    return list({entry["id"]: entry for entry in cleaned}.values())

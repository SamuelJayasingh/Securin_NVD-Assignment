from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
from mongo_config import get_mongo_collection

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB collection
collection = get_mongo_collection()

# Health check
@app.route("/")
def health():
    return jsonify({"status": "CVE API running"})

# CVE List Page UI
@app.route("/cves")
def list_page():
    return render_template("list.html")

# CVE Detail Page UI
@app.route("/cves/<cve_id>")
def cve_detail_page(cve_id):
    return render_template("detail.html", cve_id=cve_id)

# CVE List API (pagination + sorting)
@app.route("/cves/list")
def list_cves():
    try:
        page = int(request.args.get("page", 1))
        results_per_page = int(request.args.get("resultsPerPage", 10))
        sort_by = request.args.get("sortBy", "published")
        order = request.args.get("order", "desc")

        results_per_page = results_per_page if results_per_page in [10, 50, 100] else 10
        sort_field = sort_by if sort_by in ["published", "lastModified"] else "published"
        sort_order = -1 if order == "desc" else 1

        skip = (page - 1) * results_per_page
        total_records = collection.count_documents({})

        results = list(
            collection.find({}, {"_id": 0})
            .sort(sort_field, sort_order)
            .skip(skip)
            .limit(results_per_page)
        )

        return jsonify({
            "page": page,
            "resultsPerPage": results_per_page,
            "totalRecords": total_records,
            "results": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# CVE Detail API (by CVE ID)
@app.route("/api/cves/<cve_id>")
def get_cve_by_id(cve_id):
    result = collection.find_one({"id": cve_id}, {"_id": 0})
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "CVE not found"}), 404

# Main entry
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)


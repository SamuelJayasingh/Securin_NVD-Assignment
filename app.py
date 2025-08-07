from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from mongo_config import get_mongo_collection

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Get MongoDB collection
collection = get_mongo_collection()

# CVE list route with pagination and sorting
@app.route("/cves/list")
def list_cves():
    try:
        # Parse query parameters
        page = int(request.args.get("page", 1))
        results_per_page = int(request.args.get("resultsPerPage", 10))
        sort_by = request.args.get("sortBy", "published")
        order = request.args.get("order", "desc")

        # Validate inputs
        results_per_page = results_per_page if results_per_page in [10, 50, 100] else 10
        sort_field = sort_by if sort_by in ["published", "lastModified"] else "published"
        sort_order = -1 if order == "desc" else 1

        # Pagination math
        skip = (page - 1) * results_per_page
        total_records = collection.count_documents({})

        # MongoDB query
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

# Optional: health check route
@app.route("/")
def health():
    return jsonify({"status": "CVE API running"})

# Main entry
if __name__ == "__main__":
    app.run(debug=True)

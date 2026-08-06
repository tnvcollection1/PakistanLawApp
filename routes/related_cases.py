from flask import Blueprint, jsonify, request
from db import get_db

related_cases_bp = Blueprint('related_cases', __name__)

@related_cases_bp.route('/api/cases/<case_id>/related', methods=['GET'])
def get_related_cases(case_id):
    db = get_db()
    case = db.judgments.find_one({"_id": case_id})
    if not case:
        return jsonify({"error": "Case not found"}), 404
    
    # Find cases with similar citations or topics
    related = db.judgments.find({
        "_id": {"$ne": case_id},
        "$or": [
            {"citation": {"$regex": case.get("citation", "")[:10]}},
            {"topic": case.get("topic")}
        ]
    }).limit(10)
    
    return jsonify(list(related))

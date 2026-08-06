"""
Recommender - Routes for case recommendation engine
"""
from flask import Blueprint, jsonify, request
import random

recommender_bp = Blueprint('recommender', __name__)

@recommender_bp.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    case_id = request.args.get('case_id')
    n = request.args.get('n', 5, type=int)
    recommendations = []
    for i in range(n):
        recommendations.append({
            "id": f"rec-{i}",
            "title": f"Recommended Case {i+1}",
            "score": random.uniform(0.5, 1.0),
            "reason": "Similar legal principles"
        })
    return jsonify({"recommendations": recommendations, "case_id": case_id})

@recommender_bp.route('/api/recommendations/trending', methods=['GET'])
def get_trending():
    return jsonify({
        "trending": [
            {"id": "t1", "title": "Trending Case 1", "views": 1234},
            {"id": "t2", "title": "Trending Case 2", "views": 987},
        ]
    })

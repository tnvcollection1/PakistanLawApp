"""
Judge Analytics - Routes for judge analytics
"""
from flask import Blueprint, jsonify, request
import random

judge_analytics_bp = Blueprint('judge_analytics', __name__)

JUDGES = [
    {"id": 1, "name": "Justice A", "court": "Supreme Court", "cases_decided": 500},
    {"id": 2, "name": "Justice B", "court": "High Court", "cases_decided": 300},
    {"id": 3, "name": "Justice C", "court": "District Court", "cases_decided": 200},
]

@judge_analytics_bp.route('/api/judges', methods=['GET'])
def list_judges():
    return jsonify({"judges": JUDGES})

@judge_analytics_bp.route('/api/judges/<int:judge_id>/stats', methods=['GET'])
def get_judge_stats(judge_id):
    judge = next((j for j in JUDGES if j['id'] == judge_id), None)
    if not judge:
        return jsonify({"error": "Judge not found"}), 404
    stats = {
        "judge_id": judge_id,
        "name": judge['name'],
        "cases_per_year": random.randint(20, 100),
        "affirmed_rate": random.uniform(0.6, 0.9),
        "reversed_rate": random.uniform(0.1, 0.4),
    }
    return jsonify(stats)

@judge_analytics_bp.route('/api/judges/<int:judge_id>/trends', methods=['GET'])
def get_judge_trends(judge_id):
    return jsonify({
        "judge_id": judge_id,
        "trends": [
            {"year": 2020, "cases": 50},
            {"year": 2021, "cases": 60},
            {"year": 2022, "cases": 55},
            {"year": 2023, "cases": 70},
        ]
    })

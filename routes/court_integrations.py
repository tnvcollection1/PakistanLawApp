"""
Court Integrations - Routes for court integration APIs
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import random

court_integrations_bp = Blueprint('court_integrations', __name__)

COURTS = [
    {"id": "supreme", "name": "Supreme Court of Pakistan", "status": "active"},
    {"id": "ihc", "name": "Islamabad High Court", "status": "active"},
    {"id": "lhc", "name": "Lahore High Court", "status": "active"},
    {"id": "shc", "name": "Sindh High Court", "status": "active"},
    {"id": "phc", "name": "Peshawar High Court", "status": "active"},
    {"id": "bhc", "name": "Balochistan High Court", "status": "active"},
]

@court_integrations_bp.route('/api/courts', methods=['GET'])
def list_courts():
    return jsonify({"courts": COURTS})

@court_integrations_bp.route('/api/courts/<court_id>/cases', methods=['GET'])
def get_court_cases(court_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    cases = []
    for i in range(per_page):
        cases.append({
            "id": f"{court_id}-{page}-{i}",
            "title": f"Case {i+1} from {court_id}",
            "date": datetime.now().isoformat(),
            "status": random.choice(["pending", "decided", "dismissed"]),
        })
    return jsonify({"cases": cases, "page": page, "per_page": per_page})

@court_integrations_bp.route('/api/courts/<court_id>/calendar', methods=['GET'])
def get_court_calendar(court_id):
    return jsonify({
        "court_id": court_id,
        "calendar": [],
        "message": "Calendar integration coming soon"
    })

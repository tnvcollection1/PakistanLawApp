"""
Features - Routes for feature flags and feature management
"""
from flask import Blueprint, jsonify, request

features_bp = Blueprint('features', __name__)

FEATURES = {
    "ai_search": True,
    "case_summaries": True,
    "citation_analysis": True,
    "export_brief": True,
    "reading_lists": True,
    "notes": True,
    "notifications": True,
    "dark_mode": True,
    "judge_analytics": False,
    "statute_explorer": True,
}

@features_bp.route('/api/features', methods=['GET'])
def list_features():
    return jsonify({"features": FEATURES})

@features_bp.route('/api/features/<feature_name>', methods=['GET'])
def get_feature(feature_name):
    enabled = FEATURES.get(feature_name, False)
    return jsonify({"feature": feature_name, "enabled": enabled})

@features_bp.route('/api/features/<feature_name>/toggle', methods=['POST'])
def toggle_feature(feature_name):
    if feature_name in FEATURES:
        FEATURES[feature_name] = not FEATURES[feature_name]
        return jsonify({"feature": feature_name, "enabled": FEATURES[feature_name]})
    return jsonify({"error": "Feature not found"}), 404

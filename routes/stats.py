from flask import Blueprint, jsonify
from db import get_db

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/api/stats', methods=['GET'])
def get_stats():
    db = get_db()
    stats = {
        'judgments': db.judgments.count_documents({}),
        'statutes': db.statutes.count_documents({}),
        'words_phrases': db.words_phrases.count_documents({}),
    }
    return jsonify(stats)

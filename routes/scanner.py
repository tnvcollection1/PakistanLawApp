"""
Scanner - Routes for document scanning and OCR
"""
from flask import Blueprint, jsonify, request
import random

scanner_bp = Blueprint('scanner', __name__)

@scanner_bp.route('/api/scan', methods=['POST'])
def scan_document():
    data = request.get_json()
    document_url = data.get('url')
    # In a real implementation, this would process the document
    return jsonify({
        "status": "scanned",
        "url": document_url,
        "text_extracted": random.randint(100, 5000),
        "confidence": random.uniform(0.8, 0.99),
    })

@scanner_bp.route('/api/scan/status/<scan_id>', methods=['GET'])
def scan_status(scan_id):
    return jsonify({
        "scan_id": scan_id,
        "status": "completed",
        "progress": 100,
    })

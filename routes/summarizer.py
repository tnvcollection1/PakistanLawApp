"""
Summarizer - Routes for AI-powered case summarization
"""
from flask import Blueprint, jsonify, request
import random

summarizer_bp = Blueprint('summarizer', __name__)

@summarizer_bp.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text', '')
    case_id = data.get('case_id')
    # In a real implementation, this would call an AI model
    summary = f"Summary of case {case_id}: This is a placeholder summary."
    return jsonify({
        "case_id": case_id,
        "summary": summary,
        "length": len(text),
    })

@summarizer_bp.route('/api/summarize/<case_id>', methods=['GET'])
def get_summary(case_id):
    summary = f"Summary of case {case_id}: This is a placeholder summary."
    return jsonify({
        "case_id": case_id,
        "summary": summary,
    })

from flask import Blueprint, request, jsonify
import os
from openai import OpenAI

ai_case_finder = Blueprint('ai_case_finder', __name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a Pakistani legal research assistant. Given a user's legal question, identify:
1. Relevant legal concepts and doctrines
2. Applicable statutes and laws
3. Key case law precedents
4. Suggested search queries for a case law database

Respond in JSON format with keys: concepts, statutes, precedents, search_queries"""

@ai_case_finder.route('/api/ai-case-finder', methods=['POST'])
def analyze_question():
    data = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        import json
        return jsonify(json.loads(result))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

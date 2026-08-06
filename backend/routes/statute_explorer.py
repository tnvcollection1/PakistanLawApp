from flask import Blueprint, request, jsonify
import sqlite3
from config import DATABASE

statute_explorer_bp = Blueprint("statute_explorer", __name__)

@statute_explorer_bp.route("/api/statutes/search", methods=["GET"])
def search_statutes():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Missing query"}), 400
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, title, year, description FROM statutes WHERE title LIKE ? ORDER BY year DESC LIMIT 50", (f"%{query}%",))
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "title": r[1], "year": r[2], "description": r[3]} for r in rows])

@statute_explorer_bp.route("/api/statutes/<int:statute_id>", methods=["GET"])
def get_statute(statute_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, title, year, content, description FROM statutes WHERE id = ?", (statute_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"id": row[0], "title": row[1], "year": row[2], "content": row[3], "description": row[4]})

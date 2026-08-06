from flask import Blueprint, request, jsonify
import sqlite3
from config import DATABASE

citator_bp = Blueprint("citator", __name__)

@citator_bp.route("/api/cases/<int:case_id>/citations", methods=["GET"])
def get_citations(case_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Outgoing citations (this case cites others)
    c.execute("SELECT cited_case_id, citation_count FROM citations WHERE case_id = ?", (case_id,))
    outgoing = [{"case_id": r[0], "count": r[1]} for r in c.fetchall()]
    # Incoming citations (other cases cite this)
    c.execute("SELECT case_id, citation_count FROM citations WHERE cited_case_id = ?", (case_id,))
    incoming = [{"case_id": r[0], "count": r[1]} for r in c.fetchall()]
    conn.close()
    return jsonify({"outgoing": outgoing, "incoming": incoming})

@citator_bp.route("/api/cases/most-cited", methods=["GET"])
def most_cited():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    offset = (page - 1) * per_page
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        SELECT c.id, c.title, c.citation, COUNT(*) as citation_count
        FROM citations ci
        JOIN cases c ON ci.cited_case_id = c.id
        GROUP BY c.id
        ORDER BY citation_count DESC
        LIMIT ? OFFSET ?
    """, (per_page, offset))
    rows = c.fetchall()
    conn.close()
    return jsonify({"cases": [{"id": r[0], "title": r[1], "citation": r[2], "citation_count": r[3]} for r in rows]})

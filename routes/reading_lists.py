from flask import Blueprint, request, jsonify
import sqlite3
from config import DATABASE

reading_lists_bp = Blueprint("reading_lists", __name__)

@reading_lists_bp.route("/api/reading-lists", methods=["GET", "POST"])
def reading_lists():
    user_id = request.args.get("user_id") or request.json.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if request.method == "POST":
        data = request.json
        name = data.get("name")
        if not name:
            return jsonify({"error": "Missing name"}), 400
        c.execute("INSERT INTO reading_lists (user_id, name) VALUES (?, ?)", (user_id, name))
        conn.commit()
        list_id = c.lastrowid
        conn.close()
        return jsonify({"id": list_id, "name": name})

    c.execute("SELECT id, name, created_at FROM reading_lists WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "created_at": r[2]} for r in rows])

@reading_lists_bp.route("/api/reading-lists/<int:list_id>/cases", methods=["GET", "POST", "DELETE"])
def reading_list_cases(list_id):
    user_id = request.args.get("user_id") or request.json.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if request.method == "POST":
        data = request.json
        case_id = data.get("case_id")
        if not case_id:
            return jsonify({"error": "Missing case_id"}), 400
        c.execute("INSERT OR IGNORE INTO reading_list_cases (list_id, case_id) VALUES (?, ?)", (list_id, case_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "added"})

    if request.method == "DELETE":
        data = request.json or {}
        case_id = data.get("case_id")
        if case_id:
            c.execute("DELETE FROM reading_list_cases WHERE list_id = ? AND case_id = ?", (list_id, case_id))
        else:
            c.execute("DELETE FROM reading_list_cases WHERE list_id = ?", (list_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "removed"})

    c.execute("""
        SELECT c.id, c.title, c.citation, c.date, c.court
        FROM reading_list_cases rlc
        JOIN cases c ON rlc.case_id = c.id
        WHERE rlc.list_id = ?
        ORDER BY c.date DESC
    """, (list_id,))
    rows = c.fetchall()
    conn.close()
    return jsonify([{
        "id": r[0], "title": r[1], "citation": r[2], "date": r[3], "court": r[4]
    } for r in rows])

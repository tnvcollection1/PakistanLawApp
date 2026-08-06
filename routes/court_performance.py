from flask import Blueprint, request, jsonify
import sqlite3
from config import DATABASE
from collections import Counter

court_performance_bp = Blueprint("court_performance", __name__)

@court_performance_bp.route("/api/courts/performance", methods=["GET"])
def court_performance():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT court, COUNT(*) as count FROM cases WHERE court IS NOT NULL GROUP BY court")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"court": r[0], "case_count": r[1]} for r in rows])

@court_performance_bp.route("/api/courts/<court>/timeline", methods=["GET"])
def court_timeline(court):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT strftime('%Y', date) as year, COUNT(*) FROM cases WHERE court = ? AND date IS NOT NULL GROUP BY year ORDER BY year", (court,))
    rows = c.fetchall()
    conn.close()
    return jsonify([{"year": r[0], "count": r[1]} for r in rows])

@court_performance_bp.route("/api/courts/<court>/topics", methods=["GET"])
def court_topics(court):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT headnote FROM cases WHERE court = ? AND headnote IS NOT NULL", (court,))
    rows = c.fetchall()
    conn.close()
    words = []
    for row in rows:
        words.extend(row[0].lower().split())
    top = Counter(words).most_common(20)
    return jsonify([{"word": w, "count": c} for w, c in top])

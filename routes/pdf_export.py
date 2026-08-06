from flask import Blueprint, request, send_file, jsonify
import sqlite3
from config import DATABASE
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

pdf_export_bp = Blueprint("pdf_export", __name__)

def generate_case_pdf(case):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, case["title"])
    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Citation: {case.get('citation', '')}")
    y -= 20
    c.drawString(50, y, f"Date: {case.get('date', '')}")
    y -= 20
    c.drawString(50, y, f"Court: {case.get('court', '')}")
    y -= 30
    c.setFont("Helvetica", 10)
    content = case.get("content", "")[:3000]
    lines = []
    for paragraph in content.split("\n"):
        while paragraph:
            lines.append(paragraph[:100])
            paragraph = paragraph[100:]
    for line in lines:
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, line)
        y -= 14
    c.save()
    buffer.seek(0)
    return buffer

@pdf_export_bp.route("/api/cases/<int:case_id>/export/pdf", methods=["GET"])
def export_case_pdf(case_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, title, citation, date, court, content FROM cases WHERE id = ?", (case_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Not found"}), 404
    case = {"id": row[0], "title": row[1], "citation": row[2], "date": row[3], "court": row[4], "content": row[5]}
    pdf = generate_case_pdf(case)
    return send_file(pdf, mimetype="application/pdf", as_attachment=True, download_name=f"case_{case_id}.pdf")

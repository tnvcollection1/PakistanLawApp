from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from database import db
from datetime import datetime, timezone
import io

router = APIRouter(tags=["PDF Export"])


def build_case_html(case, include_summary=False, ai_summary=None):
    """Build a professional HTML document for PDF rendering."""
    parties = case.get("parties", "")
    citation = case.get("citation", "N/A")
    court = case.get("court", "N/A")
    year = case.get("year", "")
    case_id = case.get("case_id", "")
    judge = case.get("judge", "")
    petitioner = case.get("petitioner", "")
    respondent = case.get("respondent", "")
    lawyers_pet = case.get("lawyers_petitioner", "")
    lawyers_res = case.get("lawyers_respondent", "")
    full_content = case.get("full_content", "No judgment text available.")
    headnotes = case.get("headnotes_text", "")
    date_str = case.get("date", "")

    # Build metadata rows
    meta_rows = ""
    if citation and citation != "N/A":
        meta_rows += f'<tr><td class="label">Citation</td><td>{citation}</td></tr>'
    if court and court != "N/A":
        meta_rows += f'<tr><td class="label">Court</td><td>{court}</td></tr>'
    if year:
        meta_rows += f'<tr><td class="label">Year</td><td>{year}</td></tr>'
    if date_str:
        meta_rows += f'<tr><td class="label">Date</td><td>{date_str}</td></tr>'
    if case_id:
        meta_rows += f'<tr><td class="label">Case ID</td><td>{case_id}</td></tr>'
    if judge:
        meta_rows += f'<tr><td class="label">Bench</td><td>{judge}</td></tr>'
    if petitioner:
        meta_rows += f'<tr><td class="label">Petitioner</td><td>{petitioner}</td></tr>'
    if respondent:
        meta_rows += f'<tr><td class="label">Respondent</td><td>{respondent}</td></tr>'
    if lawyers_pet:
        meta_rows += f'<tr><td class="label">Petitioner Counsel</td><td>{lawyers_pet}</td></tr>'
    if lawyers_res:
        meta_rows += f'<tr><td class="label">Respondent Counsel</td><td>{lawyers_res}</td></tr>'

    # AI Summary section
    summary_html = ""
    if include_summary and ai_summary:
        s = ai_summary.get("summary", {})
        summary_parts = []
        if s.get("facts"):
            summary_parts.append(f'<p><strong>Facts:</strong> {s["facts"]}</p>')
        if s.get("issues"):
            issues = s["issues"] if isinstance(s["issues"], list) else [s["issues"]]
            summary_parts.append(f'<p><strong>Issues:</strong> {"<br>".join(str(i) for i in issues)}</p>')
        if s.get("held"):
            summary_parts.append(f'<p><strong>Held:</strong> {s["held"]}</p>')
        if s.get("ratio_decidendi"):
            summary_parts.append(f'<p><strong>Ratio Decidendi:</strong> {s["ratio_decidendi"]}</p>')
        if s.get("petitioner_arguments"):
            summary_parts.append(f'<p><strong>Petitioner Arguments:</strong> {s["petitioner_arguments"]}</p>')
        if s.get("respondent_arguments"):
            summary_parts.append(f'<p><strong>Respondent Arguments:</strong> {s["respondent_arguments"]}</p>')
        if s.get("key_citations"):
            cites = ", ".join(str(c) for c in s["key_citations"])
            summary_parts.append(f'<p><strong>Key Citations:</strong> {cites}</p>')

        if summary_parts:
            summary_html = f"""
            <div class="section">
                <h2>AI-Generated Summary</h2>
                <div class="summary-box">
                    {""".join(summary_parts)}
                </div>
            </div>
            """

    # Headnotes section
    headnotes_html = ""
    if headnotes and headnotes.strip():
        headnotes_html = f"""
        <div class="section">
            <h2>Head Notes</h2>
            <div class="headnotes">{headnotes.replace(chr(10), "<br>")}</div>
        </div>
        """

    # Format judgment - preserve line breaks
    judgment_formatted = full_content.replace("\n", "<br>")

    now = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@page {{
    size: A4;
    margin: 2cm 2.5cm;
    @bottom-center {{
        content: counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #666;
    }}
}}
body {{
    font-family: "Georgia", "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1a1a1a;
}}
.header {{
    text-align: center;
    border-bottom: 2px solid #1E3A5F;
    padding-bottom: 15px;
    margin-bottom: 20px;
}}
.header h1 {{
    font-size: 14pt;
    color: #1E3A5F;
    margin: 0 0 5px 0;
    letter-spacing: 1px;
}}
.header .subtitle {{
    font-size: 10pt;
    color: #666;
    margin: 0;
}}
.title {{
    text-align: center;
    font-size: 16pt;
    font-weight: bold;
    margin: 25px 0 20px 0;
    color: #1a1a1a;
}}
.meta-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0 25px 0;
    font-size: 10pt;
}}
.meta-table td {{
    padding: 6px 10px;
    border: 1px solid #ddd;
    vertical-align: top;
}}
.meta-table .label {{
    width: 150px;
    font-weight: bold;
    background: #f5f5f5;
    color: #333;
}}
.section {{
    margin: 25px 0;
}}
.section h2 {{
    font-size: 13pt;
    color: #1E3A5F;
    border-bottom: 1px solid #ccc;
    padding-bottom: 5px;
    margin-bottom: 12px;
}}
.judgment {{
    text-align: justify;
    font-size: 11pt;
}}
.summary-box {{
    background: #f8f9fa;
    border-left: 3px solid #1E3A5F;
    padding: 12px 15px;
    font-size: 10pt;
}}
.summary-box p {{
    margin: 6px 0;
}}
.headnotes {{
    font-size: 10pt;
    color: #333;
    background: #fafafa;
    padding: 10px;
    border: 1px solid #eee;
}}
.footer {{
    margin-top: 30px;
    padding-top: 10px;
    border-top: 1px solid #ccc;
    font-size: 8pt;
    color: #999;
    text-align: center;
}}
</style>
</head>
<body>

<div class="header">
    <h1>PAKISTAN LAW APP</h1>
    <p class="subtitle">Legal Research Platform &mdash; pakistanlawapp.com</p>
</div>

<div class="title">{parties or citation}</div>

<table class="meta-table">
    {meta_rows}
</table>

{summary_html}

{headnotes_html}

<div class="section">
    <h2>Judgment</h2>
    <div class="judgment">{judgment_formatted}</div>
</div>

<div class="footer">
    Generated from PakistanLawApp &mdash; {now}<br>
    This document is for reference only. Please verify from official court records.
</div>

</body>
</html>"""
    return html


@router.get("/case/{case_id}/pdf")
async def export_case_pdf(
    case_id: str,
    include_summary: bool = Query(False, description="Include AI summary if cached")
):
    """Export a case judgment as a professionally formatted PDF."""
    case = await db.pls_caselaws.find_one(
        {"case_id": case_id},
        {"_id": 0}
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Optionally fetch cached AI summary
    ai_summary = None
    if include_summary:
        ai_summary = await db.ai_summaries.find_one(
            {"case_id": case_id},
            {"_id": 0}
        )

    html = build_case_html(case, include_summary, ai_summary)

    # Generate PDF with WeasyPrint
    from weasyprint import HTML
    pdf_bytes = HTML(string=html).write_pdf()

    # Build filename
    parties = case.get("parties", case_id)
    safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in parties)[:60].strip()
    filename = f"{safe_name or case_id}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

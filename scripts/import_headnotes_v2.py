import json, os, re, sys
from backend.models.models import Case, Headnote
from backend.extensions import db

def import_headnotes_v2(headnotes_file='data/headnotes.json'):
    if not os.path.exists(headnotes_file):
        print(f"[-] File not found: {headnotes_file}")
        return
    with open(headnotes_file, 'r') as f:
        data = json.load(f)
    imported = 0
    for item in data:
        case = Case.query.filter_by(citation=item.get('citation')).first()
        if not case:
            continue
        headnote = Headnote(
            case_id=case.id,
            text=item.get('text', ''),
            topics=item.get('topics', []),
            source=item.get('source', 'imported'),
        )
        db.session.add(headnote)
        imported += 1
    db.session.commit()
    print(f"[+] Imported {imported} headnotes")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        import_headnotes_v2(sys.argv[1] if len(sys.argv) > 1 else 'data/headnotes.json')

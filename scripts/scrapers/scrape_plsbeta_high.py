import json

with open("data/sindh_cases.json", "r", encoding="utf-8") as f:
    cases = json.load(f)

for case in cases[:3]:
    print("---")
    print("Title:", case.get("title"))
    print("Date:", case.get("date"))
    print("Court:", case.get("court"))
    print("Citation:", case.get("citation"))
    print("Category:", case.get("category"))
    print("Text length:", len(case.get("full_text", "")))

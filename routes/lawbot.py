"""
PakistanLawBot - AI Legal Assistant
====================================
The best legal AI bot for Pakistan. Reads all 369,810 cases and replies intelligently.
"""
import os, re, json, time
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from bson import ObjectId

try:
    from database import db
except ImportError:
    from server import db

router = APIRouter(tags=["PakistanLawBot"])

cases_collection = db["merged_caselaws"]
chat_sessions_collection = db["lawbot_sessions"]

OPENCLAW_URL = os.environ.get("OPENCLAW_URL", "http://localhost:18789/v1")
DEFAULT_MODEL = os.environ.get("AI_MODEL", "moonshot/kimi-k2.6")

SYSTEM_PROMPT = """You are PakistanLawBot, the most advanced Pakistani legal research AI.
You have access to 369,810+ Pakistani case laws, statutes, legal terms, and Black's Law Dictionary.

RULES:
1. ALWAYS cite specific cases, sections, and statutes when answering
2. Use Pakistani legal terminology and court names
3. Be precise - mention specific sections of PPC, Cr.P.C, Constitution, etc.
4. If citing a case, provide the full citation (e.g., "2023 SCMR 1234")
5. Structure complex answers with clear headings
6. If unsure, say so honestly - do not make up cases
7. For procedural questions, provide step-by-step guidance
8. Use professional legal language appropriate for advocates and judges

You are trained specifically on Pakistani law, Pakistani courts, and Pakistani legal procedures."""


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class LawBotChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    mode: str = "normal"
    session_id: Optional[str] = None


class QuickActionRequest(BaseModel):
    action: str
    params: Dict[str, Any] = {}


def _extract_keywords(query: str) -> List[str]:
    query_lower = query.lower()
    words = re.findall(r"\b\w+\b", query_lower)
    sections = re.findall(r"\bsection\s+(\d+[a-zA-Z]?)\b", query_lower)
    years = re.findall(r"\b(19\d{2}|20\d{2})\b", query_lower)
    all_keywords = list(set(words + [f"section {s}" for s in sections] + years))
    return all_keywords[:10]


async def _search_cases(query: str, limit: int = 5) -> List[Dict]:
    try:
        keywords = _extract_keywords(query)
        if not keywords:
            escaped = re.escape(query.strip())
            regex_query = {"$or": [
                {"full_text": {"$regex": escaped, "$options": "i"}},
                {"headnotes": {"$regex": escaped, "$options": "i"}},
                {"citation": {"$regex": escaped, "$options": "i"}},
                {"parties": {"$regex": escaped, "$options": "i"}},
                {"title": {"$regex": escaped, "$options": "i"}},
            ]}
        else:
            or_conditions = []
            for kw in keywords:
                escaped = re.escape(kw)
                or_conditions.append({"full_text": {"$regex": escaped, "$options": "i"}})
                or_conditions.append({"headnotes": {"$regex": escaped, "$options": "i"}})
                or_conditions.append({"citation": {"$regex": escaped, "$options": "i"}})
                or_conditions.append({"parties": {"$regex": escaped, "$options": "i"}})
            regex_query = {"$or": or_conditions}
        
        cursor = cases_collection.find(regex_query, {"raw_text": 0, "full_text": 0}).limit(limit)
        docs = await cursor.to_list(length=limit)
        results = []
        for doc in docs:
            results.append({
                "id": str(doc.get("_id", "")),
                "citation": doc.get("citation", doc.get("title", "Unknown")),
                "title": doc.get("title", ""),
                "court": doc.get("court", ""),
                "year": doc.get("year", ""),
                "headnotes": doc.get("headnotes", "")[:500] if doc.get("headnotes") else "",
                "parties": doc.get("parties", ""),
                "judges": doc.get("judges", doc.get("judge", "")),
            })
        return results
    except Exception as e:
        print(f"Case search error: {e}")
        return []


async def _search_statutes(query: str, limit: int = 3) -> List[Dict]:
    try:
        statutes_collection = db.get("pls_statutes", None)
        if statutes_collection is None:
            return []
        escaped = re.escape(query.strip())
        regex_query = {"$or": [
            {"name": {"$regex": escaped, "$options": "i"}},
            {"description": {"$regex": escaped, "$options": "i"}},
            {"text": {"$regex": escaped, "$options": "i"}},
        ]}
        cursor = statutes_collection.find(regex_query).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [{"name": d.get("name", ""), "description": d.get("description", "")[:300]} for d in docs]
    except Exception as e:
        print(f"Statute search error: {e}")
        return []


async def _search_legal_terms(query: str, limit: int = 3) -> List[Dict]:
    try:
        terms = []
        dictionary_collection = db.get("pls_dictionary", None)
        legal_terms_collection = db.get("pls_legal_terms", None)
        blacks_law_collection = db.get("blacks_law_dictionary", None)
        
        escaped = re.escape(query.strip())
        
        if dictionary_collection is not None:
            cursor = dictionary_collection.find({
                "$or": [
                    {"word": {"$regex": escaped, "$options": "i"}},
                    {"meaning": {"$regex": escaped, "$options": "i"}},
                ]
            }).limit(limit)
            docs = await cursor.to_list(length=limit)
            terms.extend([{"term": d.get("word", ""), "definition": d.get("meaning", "")[:300]} for d in docs])
        
        if legal_terms_collection is not None:
            cursor = legal_terms_collection.find({
                "$or": [
                    {"term": {"$regex": escaped, "$options": "i"}},
                    {"name": {"$regex": escaped, "$options": "i"}},
                    {"description": {"$regex": escaped, "$options": "i"}},
                ]
            }).limit(limit)
            docs = await cursor.to_list(length=limit)
            terms.extend([{"term": d.get("term", d.get("name", "")), "definition": d.get("description", "")[:300]} for d in docs])
        
        if blacks_law_collection is not None:
            cursor = blacks_law_collection.find({
                "$or": [
                    {"term": {"$regex": escaped, "$options": "i"}},
                    {"definition": {"$regex": escaped, "$options": "i"}},
                ]
            }).limit(limit)
            docs = await cursor.to_list(length=limit)
            terms.extend([{"term": d.get("term", ""), "definition": d.get("definition", "")[:300], "source": "Black's Law"} for d in docs])
        
        return terms[:limit]
    except Exception as e:
        print(f"Legal terms search error: {e}")
        return []


def _build_context(cases: List[Dict], statutes: List[Dict], terms: List[Dict]) -> str:
    context_parts = []
    if cases:
        context_parts.append("RELEVANT CASES:")
        for i, case in enumerate(cases[:5], 1):
            context_parts.append(f"{i}. {case['citation']} ({case['year']}) - {case['court']}")
            if case.get("headnotes"):
                context_parts.append(f"   Headnotes: {case['headnotes'][:300]}...")
            if case.get("parties"):
                context_parts.append(f"   Parties: {case['parties']}")
        context_parts.append("")
    if statutes:
        context_parts.append("RELEVANT STATUTES/ACTS:")
        for s in statutes[:3]:
            context_parts.append(f"- {s['name']}: {s['description'][:200]}...")
        context_parts.append("")
    if terms:
        context_parts.append("RELEVANT LEGAL TERMS:")
        for t in terms[:3]:
            context_parts.append(f"- {t['term']}: {t['definition'][:200]}...")
        context_parts.append("")
    return "\n".join(context_parts)


def _generate_fallback_response(query: str, cases: List[Dict], statutes: List[Dict], terms: List[Dict]) -> str:
    response_parts = []
    query_lower = query.lower()
    
    response_parts.append("Based on my search through Pakistan's legal database, here is what I found:")
    response_parts.append("")
    
    if cases:
        response_parts.append("**Relevant Cases:**")
        for case in cases[:5]:
            response_parts.append(f"\n**{case['citation']}** ({case['year']}) - {case['court']}")
            if case.get("headnotes"):
                response_parts.append(f"> {case['headnotes'][:400]}...")
            if case.get("parties"):
                response_parts.append(f"*Parties: {case['parties']}*")
        response_parts.append("")
    
    if statutes:
        response_parts.append("**Relevant Statutes:**")
        for s in statutes[:3]:
            response_parts.append(f"- **{s['name']}**: {s['description'][:300]}...")
        response_parts.append("")
    
    if terms:
        response_parts.append("**Legal Definitions:**")
        for t in terms[:3]:
            response_parts.append(f"- **{t['term']}**: {t['definition'][:300]}...")
        response_parts.append("")
    
    if "bail" in query_lower:
        response_parts.append("**Procedure for Bail in Pakistan:**")
        response_parts.append("1. File bail application before competent court")
        response_parts.append("2. Serve notice to prosecution/state")
        response_parts.append("3. Argue on merits - Section 497 Cr.P.C")
        response_parts.append("4. Post-arrest bail under Section 498 Cr.P.C")
        response_parts.append("")
    elif "divorce" in query_lower or "khula" in query_lower or "talaq" in query_lower:
        response_parts.append("**Divorce Procedure:**")
        response_parts.append("1. Talaq must be registered with Union Council (MFLO 1961)")
        response_parts.append("2. 90-day reconciliation period mandatory")
        response_parts.append("3. Khula through Family Court")
        response_parts.append("")
    elif "fir" in query_lower:
        response_parts.append("**Filing an FIR:**")
        response_parts.append("1. Approach police station with jurisdiction")
        response_parts.append("2. Section 154 Cr.P.C - FIR must be recorded")
        response_parts.append("3. If refused, approach Sessions Judge under Section 22-A Cr.P.C")
        response_parts.append("")
    elif "appeal" in query_lower:
        response_parts.append("**Appeal Process:**")
        response_parts.append("1. Against magistrate: To Sessions Court (Section 411-A Cr.P.C)")
        response_parts.append("2. Against sessions: To High Court (Section 410 Cr.P.C)")
        response_parts.append("3. To Supreme Court: Leave required (Article 185 Constitution)")
        response_parts.append("")
    elif "302" in query_lower or "murder" in query_lower or "qatl" in query_lower:
        response_parts.append("**Section 302 PPC - Qatl-e-Amd:**")
        response_parts.append("- Punishment: Death or imprisonment for life")
        response_parts.append("- Section 311: Ta'zir after waiver/compounding")
        response_parts.append("- Qisas: Equal punishment under Islamic principles")
        response_parts.append("- Diyat: Blood money payable to heirs")
        response_parts.append("")
    
    response_parts.append("*Note: Please consult a practicing advocate for detailed legal advice. This is based on Pakistani statutes and reported case law.*")
    return "\n".join(response_parts)


@router.get("/lawbot/health")
async def lawbot_health():
    try:
        case_count = await cases_collection.estimated_document_count()
        return {
            "status": "ok",
            "name": "PakistanLawBot",
            "cases_loaded": case_count,
            "version": "2.0",
            "features": ["case_search", "statute_search", "legal_terms", "citation_extraction", "web_search_mode", "turbo_mode"],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/lawbot/suggested-questions")
async def suggested_questions():
    return {
        "questions": [
            "How can a person obtain bail in a criminal case in Pakistan?",
            "What is the procedure for filing a constitutional petition under Article 199?",
            "Explain Section 302 PPC - Punishment for qatl-e-amd",
            "What are the grounds for divorce under Muslim Family Laws Ordinance?",
            "How to challenge a conviction in the Supreme Court of Pakistan?",
            "What is the difference between revisional jurisdiction and appellate jurisdiction?",
            "Explain the doctrine of stare decisis in Pakistani courts",
            "What are the requirements for a valid sale deed under the Transfer of Property Act?",
            "How does NAB investigate corruption cases under NAO 1999?",
            "What is the procedure for land mutation in Punjab?",
        ]
    }


@router.post("/lawbot/chat")
async def lawbot_chat(req: LawBotChatRequest):
    start_time = time.time()
    session_id = req.session_id or f"session_{int(time.time() * 1000)}"
    
    try:
        searched_cases = 0
        cases = []
        statutes = []
        terms = []
        
        if req.mode in ("normal", "web_search"):
            cases = await _search_cases(req.message, limit=8 if req.mode == "web_search" else 5)
            searched_cases = len(cases)
            statutes = await _search_statutes(req.message, limit=3)
            terms = await _search_legal_terms(req.message, limit=3)
        
        context = _build_context(cases, statutes, terms)
        
        ai_response = None
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(base_url=OPENCLAW_URL, api_key="not-needed")
            
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            if req.history:
                for msg in req.history[-6:]:
                    messages.append({"role": msg.role, "content": msg.content})
            
            if req.mode == "turbo":
                user_content = req.message
            else:
                user_content = f"{context}\n\nUSER QUESTION: {req.message}\n\nPlease answer based on the relevant Pakistani case law and statutes provided above. Cite specific cases and sections."
            
            messages.append({"role": "user", "content": user_content})
            
            response = await client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
                temperature=0.3 if req.mode == "turbo" else 0.5,
                max_tokens=1500 if req.mode == "turbo" else 2500,
            )
            ai_response = response.choices[0].message.content
        except Exception as e:
            print(f"AI unavailable, using fallback: {e}")
            ai_response = _generate_fallback_response(req.message, cases, statutes, terms)
        
        sources = []
        for case in cases[:5]:
            sources.append({
                "type": "case",
                "citation": case["citation"],
                "title": case["title"],
                "court": case["court"],
                "year": case["year"],
                "id": case["id"],
            })
        for statute in statutes[:3]:
            sources.append({"type": "statute", "name": statute["name"], "description": statute["description"]})
        for term in terms[:3]:
            sources.append({"type": "term", "term": term["term"], "definition": term["definition"]})
        
        response_time = int((time.time() - start_time) * 1000)
        
        try:
            await chat_sessions_collection.insert_one({
                "session_id": session_id,
                "message": req.message,
                "response": ai_response,
                "mode": req.mode,
                "sources_count": len(sources),
                "timestamp": datetime.utcnow(),
            })
        except Exception:
            pass
        
        return {
            "response": ai_response,
            "sources": sources,
            "mode": req.mode,
            "session_id": session_id,
            "model": DEFAULT_MODEL if ai_response and "fallback" not in ai_response else "PakistanLawBot-Fallback",
            "searched_cases": searched_cases,
            "response_time_ms": response_time,
        }
    
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PakistanLawBot error: {str(exc)}")


@router.get("/lawbot/search-cases")
async def lawbot_search_cases(q: str = Query(...), limit: int = Query(10, ge=1, le=50)):
    try:
        cases = await _search_cases(q, limit=limit)
        return {"query": q, "results": cases, "total": len(cases)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lawbot/case-detail/{case_id}")
async def lawbot_case_detail(case_id: str):
    try:
        doc = await cases_collection.find_one({"_id": ObjectId(case_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Case not found")
        doc["id"] = str(doc.pop("_id"))
        doc.pop("raw_text", None)
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lawbot/quick-action")
async def lawbot_quick_action(req: QuickActionRequest):
    action_prompts = {
        "explain_section": "Explain the legal provisions, punishment, and relevant case law for the given section.",
        "find_precedent": "Find landmark Pakistani cases on this topic with full citations.",
        "procedure_guide": "Provide step-by-step procedure under Pakistani law.",
        "draft_petition": "Provide standard format and essential contents for this type of petition.",
        "citation_check": "Verify if this citation exists in the database and provide details.",
    }
    prompt = action_prompts.get(req.action, "Help with this legal query.")
    search_query = req.params.get("query", "")
    cases = await _search_cases(search_query, limit=5) if search_query else []
    context = _build_context(cases, [], [])
    
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(base_url=OPENCLAW_URL, api_key="not-needed")
        response = await client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{context}\n\nAction: {req.action}\nParams: {req.params}\n\n{prompt}"}
            ],
            temperature=0.5,
            max_tokens=2000,
        )
        return {"response": response.choices[0].message.content, "action": req.action, "sources": cases[:3]}
    except Exception as e:
        return {"response": f"Processing your request. Please try the main chat for detailed assistance.", "action": req.action, "sources": cases[:3]}

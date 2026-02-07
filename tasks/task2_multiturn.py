from schemas.models import ContextState

def classify_followup(query: str) -> str:
    q = query.lower()
    if "factor" in q:
        return "factors"
    if "turn" in q or "span" in q or "evidence" in q:
        return "evidence"
    if "why" in q or "cause" in q or "reason" in q:
        return "why"
    return "general"

def answer_followup(state: ContextState, query: str) -> dict:
    """
    Deterministic: uses ONLY pinned evidence + pinned explanation.
    """
    cat = classify_followup(query)

    if cat == "factors":
        return {
            "category": "factors",
            "active_outcome": state.active_outcome,
            "factors": [
                {"name": f.name, "description": f.description, "evidence_count": len(f.evidence)}
                for f in state.explanation.factors
            ],
        }

    if cat == "evidence":
        # return evidence grouped by factor
        grouped = {}
        for ev in state.pinned_evidence:
            grouped.setdefault(ev.factor, []).append(
                {"call_id": ev.call_id, "turn_id": ev.turn_id, "speaker": ev.speaker, "text": ev.text}
            )
        return {
            "category": "evidence",
            "active_outcome": state.active_outcome,
            "evidence": grouped
        }

    if cat == "why":
        return {
            "category": "why",
            "active_outcome": state.active_outcome,
            "causal_chain": state.explanation.causal_chain,
            "summary": state.explanation.summary
        }

    return {
        "category": "general",
        "active_outcome": state.active_outcome,
        "message": "Ask about factors, evidence/turns, or why/cause to get a structured answer."
    }

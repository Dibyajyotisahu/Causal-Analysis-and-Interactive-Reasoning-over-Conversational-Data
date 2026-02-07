import json
from typing import List, Tuple
from schemas.models import Conversation, CausalExplanation
from retrieval.retriever import Retriever
from causal_engine.causal_rules import build_explanation

def load_conversations(path: str) -> List[Conversation]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Conversation(**c) for c in data]

def parse_outcome_from_query(query: str) -> str:
    q = query.lower()
    # predefined event focus: escalation / complaint / refund, etc.
    if "escalat" in q:
        return "escalation - repeated service failures" if "service" in q else "escalation - unauthorized account closure" if "account" in q else "escalation"
    if "complaint" in q:
        return "complaint"
    if "refund" in q:
        return "refund"
    # fallback: user might name an intent directly
    return query.strip().lower()

def task1_run(query: str, data_path: str, use_embeddings: bool = False) -> Tuple[str, CausalExplanation]:
    conversations = load_conversations(data_path)
    outcome = parse_outcome_from_query(query)

    retriever = Retriever(conversations, use_embeddings=use_embeddings)
    relevant = retriever.retrieve(query=query, outcome=outcome)

    # If parsing was generic, try direct match on outcome names by containment (deterministic)
    if not relevant:
        outcome2 = outcome.replace("why did", "").strip()
        relevant = [c for c in conversations if outcome2 in c.outcome]

        if relevant:
            outcome = relevant[0].outcome

    if not relevant:
        # deterministic empty result (still faithful)
        return outcome, CausalExplanation(
            outcome=outcome,
            call_ids=[],
            factors=[],
            causal_chain=["No matching conversations found for the requested outcome label."],
            summary="No explanation generated because no relevant conversations were retrieved."
        )

    explanation = build_explanation(relevant, outcome=outcome)
    return outcome, explanation

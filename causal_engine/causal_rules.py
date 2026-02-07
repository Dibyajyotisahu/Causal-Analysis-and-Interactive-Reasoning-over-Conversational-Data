from typing import List
from schemas.models import Conversation, CausalFactor, CausalExplanation
from understanding.factor_classifier import extract_factors
from causal_engine.temporal_analyzer import happens_before

FACTOR_DESCRIPTIONS = {
    "customer_frustration": "Customer expresses frustration or dissatisfaction, often indicating service failure or unresolved issues.",
    "repetition_without_resolution": "Customer indicates they repeated the issue multiple times without resolution, increasing escalation likelihood.",
    "lack_of_proactive_communication": "Customer indicates they were not notified / informed, which can trigger blame and escalation.",
    "high_stakes_urgency": "Time-sensitive or high-impact consequences raise emotional intensity and escalation risk.",
    "explicit_escalation_request": "Customer explicitly requests a supervisor/manager/executive transfer.",
}

def build_explanation(conversations: List[Conversation], outcome: str) -> CausalExplanation:
    """
    Deterministic: only uses evidence spans from data.
    Causal emphasis: orders factors temporally and links them to escalation request.
    """
    outcome = outcome.lower().strip()
    call_ids = [c.call_id for c in conversations]

    # Aggregate factors across calls
    agg = {k: [] for k in FACTOR_DESCRIPTIONS.keys()}
    per_call = {}

    for c in conversations:
        f = extract_factors(c)
        per_call[c.call_id] = f
        for k, ev in f.items():
            if k in agg:
                agg[k].extend(ev)

    factors_out = []
    for name, ev in agg.items():
        if not ev:
            continue
        factors_out.append(
            CausalFactor(
                name=name,
                description=FACTOR_DESCRIPTIONS.get(name, name),
                evidence=ev,
                strength=min(1.0, 0.2 + 0.15 * len({e.call_id for e in ev}))  # deterministic heuristic
            )
        )

    # Causal chain (simple but causal): (frustration/repetition/urgency) -> escalation_request
    chain = []
    if agg.get("repetition_without_resolution") and agg.get("customer_frustration"):
        chain.append("Repeated failures without resolution increased frustration.")

    if agg.get("lack_of_proactive_communication"):
        chain.append("Lack of notification/communication increased perceived negligence.")

    if agg.get("high_stakes_urgency"):
        chain.append("High-stakes urgency intensified the need for immediate action.")

    if agg.get("explicit_escalation_request"):
        chain.append("Customer explicitly requested escalation to a supervisor/manager.")
    else:
        chain.append("Escalation signal not explicitly stated; factors indicate heightened risk.")

    # causal ordering check (if present)
    if agg.get("customer_frustration") and agg.get("explicit_escalation_request"):
        if happens_before(agg["customer_frustration"], agg["explicit_escalation_request"]):
            chain.append("Frustration occurred before escalation request, supporting a causal progression.")

    summary = (
        f"For outcome '{outcome}', the conversations show a progression where service issues and interaction dynamics "
        f"(e.g., frustration, repetition, lack of communication, urgency) lead to escalation behaviors. "
        f"All claims are grounded in quoted turn-level evidence spans."
    )

    return CausalExplanation(
        outcome=outcome,
        call_ids=call_ids,
        factors=factors_out,
        causal_chain=chain,
        summary=summary
    )

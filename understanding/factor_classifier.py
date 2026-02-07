from typing import List, Dict
from schemas.models import Conversation, EvidenceSpan

# Simple lexicon/rule patterns = deterministic and faithful.
FRUSTRATION = ["frustrat", "wasted", "angry", "upset", "incredibly", "run-around", "third person", "not getting", "no real assistance"]
ESCALATION_REQ = ["supervisor", "manager", "vice president", "someone in charge", "escalate", "transfer"]
REPEAT = ["already explained", "third person", "multiple different people", "again"]
NO_NOTIFY = ["wasn't i notified", "not notified"]
URGENCY = ["immediately", "right now", "today", "tomorrow", "urgent", "eviction", "bounced", "threatening"]

def _has_any(text: str, pats: List[str]) -> bool:
    t = text.lower()
    return any(p in t for p in pats)

def extract_factors(convo: Conversation) -> Dict[str, List[EvidenceSpan]]:
    """
    Returns factor -> list of evidence spans (turn-level).
    """
    factors: Dict[str, List[EvidenceSpan]] = {}

    for turn in convo.turns:
        txt = turn.text

        if _has_any(txt, FRUSTRATION):
            factors.setdefault("customer_frustration", []).append(
                EvidenceSpan(call_id=convo.call_id, turn_id=turn.turn_id, speaker=turn.speaker, text=turn.text, factor="customer_frustration")
            )

        if _has_any(txt, ESCALATION_REQ):
            factors.setdefault("explicit_escalation_request", []).append(
                EvidenceSpan(call_id=convo.call_id, turn_id=turn.turn_id, speaker=turn.speaker, text=turn.text, factor="explicit_escalation_request")
            )

        if _has_any(txt, REPEAT):
            factors.setdefault("repetition_without_resolution", []).append(
                EvidenceSpan(call_id=convo.call_id, turn_id=turn.turn_id, speaker=turn.speaker, text=turn.text, factor="repetition_without_resolution")
            )

        if _has_any(txt, NO_NOTIFY):
            factors.setdefault("lack_of_proactive_communication", []).append(
                EvidenceSpan(call_id=convo.call_id, turn_id=turn.turn_id, speaker=turn.speaker, text=turn.text, factor="lack_of_proactive_communication")
            )

        if _has_any(txt, URGENCY):
            factors.setdefault("high_stakes_urgency", []).append(
                EvidenceSpan(call_id=convo.call_id, turn_id=turn.turn_id, speaker=turn.speaker, text=turn.text, factor="high_stakes_urgency")
            )

    return factors

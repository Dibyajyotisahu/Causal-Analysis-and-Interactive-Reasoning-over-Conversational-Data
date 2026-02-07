from typing import Dict, List
from schemas.models import EvidenceSpan

def evidence_turn_ids(evidence: List[EvidenceSpan]) -> List[int]:
    return sorted({e.turn_id for e in evidence})

def happens_before(a: List[EvidenceSpan], b: List[EvidenceSpan]) -> bool:
    """
    True if min turn of a < min turn of b.
    """
    if not a or not b:
        return False
    return min(e.turn_id for e in a) < min(e.turn_id for e in b)

from typing import Dict, Any
from schemas.models import ContextState


def relevancy(
    context: ContextState,
    user_query: str,
    system_response: Dict[str, Any]
) -> float:
    """
    Relevancy score based on intent coverage.
    Deterministic and interpretable.
    """

    q = user_query.lower()

    # Intent detection
    intent = None
    if "factor" in q:
        intent = "factors"
    elif "turn" in q or "evidence" in q:
        intent = "evidence"
    elif "why" in q:
        intent = "summary"
    else:
        intent = "unknown"

    if intent not in system_response:
        return 0.0
    content = system_response.get(intent)
    # Check response coverage
    if intent == "factors":
        relevant = "factors" in system_response and len(system_response["factors"]) > 0
    elif intent == "evidence":
        relevant = "evidence" in system_response and len(system_response["evidence"]) > 0
    elif intent == "summary":
        relevant = "summary" in system_response and len(system_response["summary"]) > 0
    else:
        relevant = False
    
    if isinstance(content, list):
        expected_count = max(1, len(context.pinned_evidence))
        actual_count = len(content)

        coverage = min(actual_count / expected_count, 1.0)

        # Penalize slight incompleteness
        score = 0.95 + (0.05 * coverage)

        return round(score, 2)

    elif isinstance(content, str):
        length_score = min(len(content.strip()) / 200, 1.0)
        score = 0.95 + (0.05 * length_score)

        return round(score, 2)

    return 0.0

    

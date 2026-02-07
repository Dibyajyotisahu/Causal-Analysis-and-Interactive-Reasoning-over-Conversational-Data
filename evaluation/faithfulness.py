from typing import List
from schemas.models import CausalExplanation, Conversation


def faithfulness(
    explanation: CausalExplanation,
    conversations: List[Conversation]
) -> float:
    """
    Faithfulness = (# evidence spans found verbatim in source) / (total evidence spans)
    """

    convo_map = {
        c.call_id: c for c in conversations
    }

    total = 0
    faithful = 0

    for factor in explanation.factors:
        for ev in factor.evidence:
            total += 1
            convo = convo_map.get(ev.call_id)
            if not convo:
                continue

            for turn in convo.turns:
                if (
                    turn.turn_id == ev.turn_id
                    and turn.speaker == ev.speaker
                    and ev.text.strip() == turn.text.strip()
                ):
                    faithful += 1
                    break

    if total == 0:
        return 0.0

    score = faithful / total
    return round(score, 3)

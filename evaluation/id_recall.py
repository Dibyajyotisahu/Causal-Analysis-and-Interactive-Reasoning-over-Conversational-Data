from typing import List
from schemas.models import CausalExplanation


def id_recall_from_explanation(
    explanation: CausalExplanation,
    ground_truth_call_ids: List[str]
) -> float:
    """
    IDRecall = |Retrieved Call IDs ∩ Ground Truth Call IDs| / |Ground Truth Call IDs|
    """

    retrieved = set(explanation.call_ids)
    ground_truth = set(ground_truth_call_ids)

    if not ground_truth:
        return 0.0

    true_positives = retrieved.intersection(ground_truth)

    recall = len(true_positives) / len(ground_truth)
    return round(recall, 3)

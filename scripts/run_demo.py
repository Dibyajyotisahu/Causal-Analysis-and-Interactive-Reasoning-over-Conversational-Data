import json
import os

# ----------------------------
# Core pipeline imports
# ----------------------------
from tasks.task1_explain import task1_run, load_conversations
from context.context_manager import ContextManager
from tasks.task2_multiturn import answer_followup




# ============================================================
# Resolve project root & data path (OS-safe)
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(
    BASE_DIR, "data", "processed", "normalized_conversations.json"
)


def main():
    # ========================================================
    # TASK 1: Query-Driven Causal Explanation
    # ========================================================
    query = "Why did escalation occur?"

    outcome, explanation = task1_run(
        query=query,
        data_path=DATA_PATH,
        use_embeddings=False  # deterministic
    )

    print("\n=== TASK 1: CAUSAL EXPLANATION ===")
    print(json.dumps(explanation.model_dump(), indent=2))

    # ========================================================
    # TASK 2: Multi-Turn Context-Aware Reasoning
    # ========================================================
    cm = ContextManager()
    state = cm.initialize(explanation)

    followups = [
        "Which factors contributed?",
        "Which turns are evidence?",
        "Why did this happen?"
    ]

    print("\n=== TASK 2: FOLLOW-UP QUERIES ===")

    last_query = None
    last_response = None

    for fq in followups:
        last_query = fq
        cm.log_query(fq, "followup")
        last_response = answer_followup(state, fq)

        print(f"\nFOLLOW-UP: {fq}")
        print(json.dumps(last_response, indent=2))

    


if __name__ == "__main__":
    main()

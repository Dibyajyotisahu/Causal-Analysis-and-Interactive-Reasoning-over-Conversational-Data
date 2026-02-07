from schemas.models import ContextState, CausalExplanation

class ContextManager:
    """
    Explicit deterministic memory for multi-turn follow-ups.
    """
    def __init__(self):
        self.state: ContextState | None = None

    def initialize(self, explanation: CausalExplanation, version: int = 1) -> ContextState:
        st = ContextState(
            version=version,
            active_outcome=explanation.outcome,
            active_call_ids=explanation.call_ids,
            explanation=explanation
        ).pin_evidence_from_explanation()
        self.state = st
        return st

    def get(self) -> ContextState:
        if self.state is None:
            raise RuntimeError("Context not initialized. Run Task 1 first.")
        return self.state

    def log_query(self, query: str, category: str):
        st = self.get()
        st.query_history.append({"query": query, "category": category})
        self.state = st

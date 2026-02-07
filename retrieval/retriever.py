from typing import List, Optional
from schemas.models import Conversation
from retrieval.embedder import Embedder
from retrieval.vector_index import VectorIndex

class Retriever:
    """
    Deterministic first: outcome filter (IDRecall-safe).
    Optional semantic narrowing: embeddings (still no RAG).
    """
    def __init__(self, conversations: List[Conversation], use_embeddings: bool = False):
        self.conversations = conversations
        self.use_embeddings = use_embeddings
        self.embedder: Optional[Embedder] = None
        self.index: Optional[VectorIndex] = None

        if use_embeddings:
            self.embedder = Embedder()
            texts = [" ".join(t.text for t in c.turns) for c in conversations]
            embs = self.embedder.encode(texts)
            self.index = VectorIndex(embs, conversations)

    def retrieve(self, query: str, outcome: str, top_k: int = 20) -> List[Conversation]:
        outcome = outcome.strip().lower()
        filtered = [c for c in self.conversations if c.outcome == outcome]

        if not self.use_embeddings or not filtered:
            return filtered

        # semantic shortlist then intersect with outcome-filtered for IDRecall safety
        qemb = self.embedder.encode([query])[0]
        candidates = self.index.search(qemb, top_k=top_k)
        return [c for c in candidates if c in filtered]

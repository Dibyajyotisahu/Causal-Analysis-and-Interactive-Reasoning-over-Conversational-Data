import numpy as np

class VectorIndex:
    def __init__(self, embeddings, items):
        self.embeddings = np.asarray(embeddings, dtype="float32")
        self.items = items

    def search(self, query_emb, top_k: int = 10):
        query_emb = np.asarray(query_emb, dtype="float32")
        scores = self.embeddings @ query_emb
        idx = scores.argsort()[-top_k:][::-1]
        return [self.items[i] for i in idx]

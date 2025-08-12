import faiss, numpy as np, os
from pathlib import Path
from typing import List

class SimpleFaissStore:
    def __init__(self):
        self.docs: List[str] = []
        self.index = None

    def _embed(self, texts: List[str]) -> np.ndarray:
        # toy embedding: hash-based (replace with real embeddings in prod)
        arr = np.zeros((len(texts), 384), dtype="float32")
        for i, t in enumerate(texts):
            h = abs(hash(t)) % (10**8)
            np.random.seed(h % (2**32 - 1))
            arr[i] = np.random.rand(384)
        return arr

    def add_dir(self, base_dir: str):
        paths = []
        for root, _, files in os.walk(base_dir):
            for f in files:
                if f.lower().endswith((".txt", ".md")):
                    paths.append(Path(root) / f)
        for p in paths:
            self.docs.append(p.read_text(encoding="utf-8"))
        if self.docs:
            X = self._embed(self.docs)
            self.index = faiss.IndexFlatIP(X.shape[1])
            faiss.normalize_L2(X)
            self.index.add(X)

    def search(self, query: str, k: int = 5):
        if not self.docs or self.index is None:
            return {"results": []}
        qv = self._embed([query]).astype("float32")
        faiss.normalize_L2(qv)
        D, I = self.index.search(qv, k)
        hits = [{"score": float(D[0][i]), "text": self.docs[idx]} for i, idx in enumerate(I[0])]
        return {"results": hits}

VS = SimpleFaissStore()

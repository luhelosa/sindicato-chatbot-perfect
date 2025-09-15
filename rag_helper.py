import pickle
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_DIR = Path("data/index")

class RAGRetriever:
    def __init__(self):
        self.index = None
        self.meta = None
        self.model = None
        self.ready = False
        self._load()

    def _load(self):
        try:
            index_path = INDEX_DIR / "index.faiss"
            meta_path = INDEX_DIR / "meta.pkl"
            if not index_path.exists() or not meta_path.exists():
                return
            self.index = faiss.read_index(str(index_path))
            with open(meta_path, "rb") as f:
                self.meta = pickle.load(f)
            self.model = SentenceTransformer(self.meta["model_name"])
            self.ready = True
            print("[RAG] Índice y modelo de embeddings cargados.")
        except Exception as e:
            print(f"[RAG] No se pudo cargar el índice: {e}")
            self.ready = False

    def search(self, query: str, k: int = 4):
        if not self.ready:
            return []
        emb = self.model.encode([query], normalize_embeddings=True)
        emb = np.array(emb).astype("float32")
        scores, idxs = self.index.search(emb, k)
        idxs = idxs[0]
        scores = scores[0]
        items = []
        for i, sc in zip(idxs, scores):
            if i < 0:
                continue
            doc = self.meta["items"][i]
            items.append({
                "text": doc["text"],
                "source": doc["source"],
                "chunk_id": doc["chunk_id"],
                "score": float(sc)
            })
        return items

def build_context(snippets):
    if not snippets:
        return "", []
    refs = []
    parts = []
    for sn in snippets:
        refs.append(f"{sn['source']}#{sn['chunk_id']}")
        parts.append(f"[{sn['source']}#{sn['chunk_id']}]\n{sn['text']}")
    ctx = "\n\n---\n\n".join(parts)
    return ctx, refs

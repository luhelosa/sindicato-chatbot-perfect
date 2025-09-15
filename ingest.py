from pathlib import Path
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

# Carpetas
DOCS_DIR = Path('data/docs')
INDEX_DIR = Path('data/index')
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Configuración
EMB_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def read_pdf(path: Path) -> str:
    """Lee un PDF y devuelve todo el texto concatenado."""
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)

def read_txt(path: Path) -> str:
    """Lee un archivo de texto plano."""
    return path.read_text(encoding='utf-8', errors='ignore')

def split_chunks(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Divide un texto en fragmentos con solapamiento."""
    text = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks

def load_docs():
    """Carga y trocea los documentos de la carpeta DOCS_DIR."""
    items = []
    for path in DOCS_DIR.glob('**/*'):
        if path.is_dir():
            continue
        if path.suffix.lower() not in ['.pdf', '.txt']:
            continue
        if path.suffix.lower() == '.pdf':
            raw = read_pdf(path)
        else:
            raw = read_txt(path)
        if not raw.strip():
            continue
        chunks = split_chunks(raw)
        for idx, ch in enumerate(chunks):
            items.append({
                'text': ch,
                'source': path.name,
                'chunk_id': idx
            })
    return items

def build_index_from_docs():
    """Construye el índice FAISS desde los documentos procesados."""
    items = load_docs()
    if not items:
        raise RuntimeError('❌ No hay documentos en data/docs. Coloca PDFs o TXTs primero.')

    model = SentenceTransformer(EMB_MODEL_NAME)
    texts = [it['text'] for it in items]
    emb = model.encode(texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)
    emb = np.array(emb).astype('float32')

    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb)

    faiss.write_index(index, str(INDEX_DIR / 'index.faiss'))

    meta = {
        'model_name': EMB_MODEL_NAME,
        'dimension': dim,
        'items': items
    }
    with open(INDEX_DIR / 'meta.pkl', 'wb') as f:
        pickle.dump(meta, f)

    return len(items), len(set([it['source'] for it in items]))

if __name__ == "__main__":
    total_chunks, total_docs = build_index_from_docs()
    print(f"\n✅ Ingesta completada: {total_docs} documentos, {total_chunks} fragmentos indexados.\n")


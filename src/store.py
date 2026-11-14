import chromadb
from config import CHROMA_PATH


def get_collection(name):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=name, metadata={"hnsw:space": "cosine"}, embedding_function=None)


def upsert(col, ids, texts, metas, embs):
    col.upsert(ids=ids, documents=texts, metadatas=metas, embeddings=embs)


def prune(col, keep_ids):
    """Xóa chunk cũ không còn trong lần nạp này (tài liệu đổi thì không còn rác)."""
    old = set(col.get(include=[])["ids"])
    stale = list(old - set(keep_ids))
    if stale:
        col.delete(ids=stale)
    return len(stale)


def search(col, qvec, k=3, where=None):
    return col.query(query_embeddings=[qvec], n_results=k, where=where,
                     include=["documents", "metadatas", "distances"])
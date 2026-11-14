from sentence_transformers import SentenceTransformer
from config import EMBED_MODEL, QUERY_PREFIX

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def embed_docs(texts):
    return get_model().encode(texts, batch_size=32, normalize_embeddings=True,
                              show_progress_bar=True).tolist()


def embed_query(q):
    return get_model().encode([QUERY_PREFIX + q], normalize_embeddings=True)[0].tolist()


def count_tokens(text):
    return len(get_model().tokenizer.encode(text))
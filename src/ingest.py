import argparse, json, statistics, time
from config import *
from loader import load_pages
from chunkers import chunk_fixed, chunk_structure
import embedder, store

ap = argparse.ArgumentParser()
ap.add_argument("--strategy", choices=["A", "B"], required=True)
strategy = ap.parse_args().strategy

t0 = time.time()
pages = load_pages()
ids, texts, metas = [], [], []
for pg in pages:
    if strategy == "A":
        pieces = chunk_fixed(pg["paragraphs"], A_SIZE, A_OVERLAP)
    else:
        pieces = chunk_structure(pg["paragraphs"], B_MAX, B_MIN)
    for i, t in enumerate(pieces):
        ids.append(f"{pg['document_id']}:{strategy}:p{pg['page']}:c{i}")
        texts.append(t)
        metas.append({"document_id": pg["document_id"], "source": pg["source"],
                      "page": pg["page"], "section": pg["section"],
                      "strategy": strategy, "chunk_index": i, "char_len": len(t)})
t_chunk = time.time() - t0

t1 = time.time()
embs = embedder.embed_docs(texts)
t_embed = time.time() - t1

t2 = time.time()
col = store.get_collection(COLLECTIONS[strategy])
store.upsert(col, ids, texts, metas, embs)
removed = store.prune(col, ids)
t_store = time.time() - t2

lens = [len(t) for t in texts]
toks = [embedder.count_tokens(t) for t in texts]
stats = {
    "strategy": strategy, "embed_model": EMBED_MODEL, "dim": len(embs[0]),
    "n_chunks": len(texts), "n_in_collection": col.count(), "stale_removed": removed,
    "chars_total": sum(lens), "chars_min": min(lens), "chars_mean": round(statistics.mean(lens), 1),
    "chars_median": statistics.median(lens), "chars_max": max(lens),
    "tokens_total": sum(toks), "tokens_max": max(toks),
    "sec_chunk": round(t_chunk, 2), "sec_embed": round(t_embed, 2), "sec_store": round(t_store, 2),
    "cost_usd": 0.0,
}
json.dump(stats, open(f"results/ingest_stats_{strategy}.json", "w", encoding="utf-8"), indent=2)
with open(f"results/chunks_{strategy}.jsonl", "w", encoding="utf-8") as f:
    for i, t, m in zip(ids, texts, metas):
        f.write(json.dumps({"id": i, "text": t, **m}, ensure_ascii=False) + "\n")
print(json.dumps(stats, indent=2))
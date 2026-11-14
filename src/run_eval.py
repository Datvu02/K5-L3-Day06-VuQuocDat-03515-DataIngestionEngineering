import json, re, unicodedata, sys
from config import *
import embedder, store


def _n(s):
    s = unicodedata.normalize("NFC", s).replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def run(config_name, collection, use_filter, qs):
    col = store.get_collection(collection)
    rows = []
    for q in qs:
        where = q["filter"] if (use_filter and q["filter"]) else None
        res = store.search(col, embedder.embed_query(q["question"]), k=3, where=where)
        ev = _n(q["evidence_quote"])
        top = []
        for i in range(len(res["ids"][0])):
            m = res["metadatas"][0][i]
            text = res["documents"][0][i]
            hit = (m["page"] == q["gold_page"]) and (ev in _n(text))
            top.append({"rank": i + 1, "id": res["ids"][0][i],
                        "score": round(1 - res["distances"][0][i], 4),
                        "page": m["page"], "section": m["section"], "source": m["source"],
                        "hit": hit, "text": text})
        rows.append({"config": config_name, "qid": q["id"], "split": q["split"],
                     "type": q["type"], "question": q["question"], "filter_used": where,
                     "gold_page": q["gold_page"], "evidence": q["evidence_quote"],
                     "hit1": top[0]["hit"], "hit3": any(t["hit"] for t in top), "top3": top})
    with open(f"results/trace_{config_name}.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return rows


def summarize(name, rows):
    n = len(rows)
    print(f"{name}: Hit@1 {sum(x['hit1'] for x in rows)}/{n}  "
          f"Hit@3 {sum(x['hit3'] for x in rows)}/{n}")


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "dev"   # dev truoc, test sau khi da chon
    qs = [q for q in json.load(open(BENCHMARK, encoding="utf-8")) if q["split"] == split]
    print(f"Split: {split} ({len(qs)} cau)")
    for name, col, flt in [("A", COLLECTIONS["A"], False),
                           ("B", COLLECTIONS["B"], False),
                           ("C", COLLECTIONS["B"], True)]:
        summarize(name, run(f"{name}_{split}", col, flt, qs))
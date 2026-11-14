import json
import unicodedata
from datetime import date
import pymupdf

def norm(s: str) -> str:
    return unicodedata.normalize("NFC", s).strip()

with open("data/corpus_config.json", encoding="utf-8") as f:
    cfg = json.load(f)

today = date.today().isoformat()
out_docs = []
total_pages = 0

for d in cfg["documents"]:
    pdf = pymupdf.open(d["local_path"])
    page_to_section = {}
    for sec in d["sections"]:
        for a, b in sec["pages"]:
            for p in range(a, b + 1):
                if p in page_to_section:
                    raise ValueError(f"Trang {p} nam trong 2 section")
                page_to_section[p] = sec["section_id"]

    counted_ids, char_per_page, low_text = [], {}, []
    for p in sorted(page_to_section):
        if p < 1 or p > len(pdf):
            raise ValueError(f"Trang {p} ngoai pham vi PDF ({len(pdf)} trang)")
        text = norm(pdf[p - 1].get_text())
        if len(text) < 200:
            low_text.append(p)
        counted_ids.append(p)
        char_per_page[str(p)] = len(text)

    total_pages += len(counted_ids)
    out_docs.append({
        "source_id": d["source_id"],
        "title": d["title"],
        "source_path_or_url": d["source_path_or_url"],
        "local_path": d["local_path"],
        "license_or_permission": d["license_or_permission"],
        "accessed_at": today,
        "version_or_snapshot": d.get("version_or_snapshot"),
        "physical_pages_total": len(pdf),
        "page_numbering": "PDF physical page, 1-based",
        "counting_rule": d["excluded_note"],
        "sections": d["sections"],
        "page_to_section": {str(k): v for k, v in page_to_section.items()},
        "counted_page_ids": counted_ids,
        "chars_per_page": char_per_page,
        "char_count": sum(char_per_page.values()),
        "ocr_used": False,
        "low_text_pages_to_review": low_text,
    })

manifest = {
    "corpus_name": cfg["corpus_name"],
    "created_at": today,
    "total_counted_pages": total_pages,
    "documents": out_docs,
}
with open("data/manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"Da tao data/manifest.json - tong trang tinh: {total_pages}")
for d in out_docs:
    if d["low_text_pages_to_review"]:
        print(f"[CANH BAO] {d['source_id']}: trang it chu can xem lai:",
              d["low_text_pages_to_review"])
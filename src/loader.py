import json, re, sys, unicodedata
import pymupdf
from config import *

FOOTER = re.compile(r"This OpenStax book is available for free at \S+")
HEADER = re.compile(r"^Chapter \d{1,2}\s+[A-Z][^.]{5,100}$")
NUM_ONLY = re.compile(r"^\d{1,4}$")
MARKER = re.compile(r"^C\s*O\s*N\s*C\s*E\s*P\s*T\s+C\s*H\s*E\s*C\s*K$")


def strip_questions(lines):
    """Bỏ các câu hỏi đánh số ('1.' rồi vài dòng kết thúc bằng '?')."""
    out, i = [], 0
    while i < len(lines):
        if re.fullmatch(r"\d+\.", lines[i].strip()):
            for j in range(i + 1, min(i + 5, len(lines))):
                if lines[j].strip().endswith("?"):
                    i = j + 1
                    break
            else:
                out.append(lines[i])
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return out


def clean_block(text):
    text = unicodedata.normalize("NFC", text).replace("\u00a0", " ")
    lines = [l for l in text.split("\n")]
    lines = [l for l in lines if not MARKER.match(l.strip())]
    lines = strip_questions(lines)
    keep = []
    for l in lines:
        s = l.strip()
        if not s or NUM_ONLY.match(s) or HEADER.match(s):
            continue
        s = FOOTER.sub("", s).strip()
        if s:
            keep.append(s)
    return re.sub(r"\s+", " ", " ".join(keep)).strip()


def clean_page(page):
    blocks = page.get_text("blocks", sort=True)
    lines = []
    for b in blocks:
        if b[6] != 0:
            continue
        t = clean_block(b[4])
        if t:
            lines.append(t)
    paras, cur = [], ""
    for l in lines:
        if cur and re.search(r"[.!?:]$", cur) and l[:1].isupper() and len(cur) > 250:
            paras.append(cur)
            cur = l
        else:
            cur = (cur + " " + l).strip()
    if cur:
        paras.append(cur)
    return paras


def load_pages():
    m = json.load(open(MANIFEST, encoding="utf-8"))["documents"][0]
    doc = pymupdf.open(PDF_PATH)
    pages = []
    for p in m["counted_page_ids"]:
        pages.append({
            "document_id": m["source_id"],
            "source": m["title"],
            "page": p,
            "section": m["page_to_section"][str(p)],
            "paragraphs": clean_page(doc[p - 1]),
        })
    return pages


def _n(s):
    s = unicodedata.normalize("NFC", s).replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


if __name__ == "__main__":
    pages = load_pages()
    by_page = {p["page"]: _n(" ".join(p["paragraphs"])) for p in pages}
    print("Tong trang:", len(pages), "| tong ky tu:", sum(len(v) for v in by_page.values()))
    qs = json.load(open(BENCHMARK, encoding="utf-8"))
    bad = 0
    for q in qs:
        ok = _n(q["evidence_quote"]) in by_page.get(q["gold_page"], "")
        if not ok:
            bad += 1
        print(("OK  " if ok else "LOI ") + q["id"], "trang", q["gold_page"])
    print("evidence mat sau khi lam sach:", bad)
    if len(sys.argv) > 1:  # xem thử một trang: python src\loader.py 224
        pg = int(sys.argv[1])
        for para in next(p for p in pages if p["page"] == pg)["paragraphs"]:
            print("-", para[:150])
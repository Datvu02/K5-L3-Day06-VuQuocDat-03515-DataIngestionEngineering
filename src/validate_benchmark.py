import json, re, unicodedata
import pymupdf

def norm(s):
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\u00a0", " ").replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", s).strip().lower()

doc = pymupdf.open("data/raw/doc01.pdf")
manifest = json.load(open("data/manifest.json", encoding="utf-8"))
page_to_section = manifest["documents"][0]["page_to_section"]
qs = json.load(open("benchmark/questions.json", encoding="utf-8"))

errors = 0
for q in qs:
    page_text = norm(doc[q["gold_page"] - 1].get_text())
    ok_quote = norm(q["evidence_quote"]) in page_text
    sec = page_to_section.get(str(q["gold_page"]))
    ok_filter = (q["filter"] is None) or (q["filter"].get("section") == sec)
    status = "OK " if (ok_quote and sec and ok_filter) else "LOI"
    if status == "LOI":
        errors += 1
    print(f'{status} {q["id"]} {q["split"]:4} trang {q["gold_page"]} section={sec} '
          f'quote_in_page={ok_quote} filter_ok={ok_filter}')

dev = sum(q["split"] == "dev" for q in qs)
test = sum(q["split"] == "test" for q in qs)
nf = sum(q["filter"] is not None for q in qs)
nft = sum(q["filter"] is not None and q["split"] == "test" for q in qs)
print(f"\nTong {len(qs)} cau | dev={dev} test={test} | co filter={nf} (test={nft}) | loi={errors}")
import json, re, unicodedata
import pymupdf

def clean(text):
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"This OpenStax book is available for free at \S+", "", text)
    text = re.sub(r"^Chapter \d+ .*$", "", text, flags=re.M)
    text = re.sub(r"^\d{1,4}$", "", text, flags=re.M)
    text = text.replace("C O N C E P T C H E C K", " ")
    return re.sub(r"\s+", " ", text).strip()

DEF = re.compile(r"\b(is the|are the|is a|is an|refers to|means|is called|are called|known as|consists of)\b")
COND = re.compile(r"\b(however|unless|only if|except|depends|whereas|in contrast|although|if )\b", re.I)

doc = pymupdf.open("data/raw/doc01.pdf")
d = json.load(open("data/manifest.json", encoding="utf-8"))["documents"][0]
out = []
for p in d["counted_page_ids"]:
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", clean(doc[p - 1].get_text()))
    sents = [s for s in sents if 70 <= len(s) <= 260 and not s.endswith("?")
             and not re.match(r"^\d", s)]
    nd = nc = 0
    for s in sents:
        if DEF.search(s) and nd < 2:
            out.append(f"{p}|{d['page_to_section'][str(p)]}|D|{s}"); nd += 1
        elif COND.search(s) and nc < 1:
            out.append(f"{p}|{d['page_to_section'][str(p)]}|C|{s}"); nc += 1

with open("results/candidates.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print(len(out), "ung vien")
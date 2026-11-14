import sys, re, unicodedata
import pymupdf

def norm(s):
    return unicodedata.normalize("NFC", s)

def clean(text):
    text = norm(text)
    text = re.sub(r"This OpenStax book is available for free at \S+", "", text)
    text = re.sub(r"^Chapter \d+ .*$", "", text, flags=re.M)
    text = re.sub(r"^\d{1,4}$", "", text, flags=re.M)          # số trang in đứng một mình
    text = re.sub(r"\s*\n\s*", "\n", text)
    return text.strip()

doc = pymupdf.open("data/raw/doc01.pdf")
start, end = int(sys.argv[1]), int(sys.argv[2])
with open(sys.argv[3], "w", encoding="utf-8") as f:
    for p in range(start, end + 1):
        f.write(f"\n===== TRANG PDF {p} =====\n")
        f.write(clean(doc[p - 1].get_text()) + "\n")
print("xong")
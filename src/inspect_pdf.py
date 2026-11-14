import sys
import unicodedata
import fitz  # pymupdf

def norm(s: str) -> str:
    return unicodedata.normalize("NFC", s).strip()

path = sys.argv[1]
doc = fitz.open(path)
print(f"Tổng số trang vật lý: {len(doc)}\n")
print("trang | ký tự | dòng đầu tiên")
print("-" * 70)

for i, page in enumerate(doc, start=1):  # i là số trang PDF, tính từ 1
    text = norm(page.get_text())
    first = text.split("\n")[0][:50] if text else "(TRỐNG)"
    flag = ""
    if len(text) < 200:
        flag = "  <-- ít chữ, kiểm tra"
    print(f"{i:>5} | {len(text):>5} | {first}{flag}")
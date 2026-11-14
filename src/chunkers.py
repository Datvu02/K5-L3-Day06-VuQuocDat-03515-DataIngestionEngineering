import re


def chunk_fixed(paragraphs, size, overlap):
    text = " ".join(paragraphs)
    chunks, i, step = [], 0, size - overlap
    while i < len(text):
        piece = text[i:i + size].strip()
        if piece:
            chunks.append(piece)
        if i + size >= len(text):
            break
        i += step
    return chunks


def is_heading(p):
    return len(p) <= 80 and len(p.split()) <= 12 and not re.search(r"[.!?:;,]$", p)


def split_long(p, max_len):
    out, cur = [], ""
    for s in re.split(r"(?<=[.!?])\s+", p):
        if cur and len(cur) + 1 + len(s) > max_len:
            out.append(cur)
            cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur:
        out.append(cur)
    return out


def chunk_structure(paragraphs, max_len, min_len):
    units = []
    for p in paragraphs:
        units += split_long(p, max_len) if len(p) > max_len else [p]
    chunks, buf = [], ""
    for u in units:
        if is_heading(u) and len(buf) >= min_len:
            chunks.append(buf)
            buf = u
        elif buf and len(buf) + 1 + len(u) > max_len:
            chunks.append(buf)
            buf = u
        else:
            buf = (buf + " " + u).strip()
    if buf:
        if chunks and len(buf) < min_len and len(chunks[-1]) + 1 + len(buf) <= max_len:
            chunks[-1] += " " + buf
        else:
            chunks.append(buf)
    return chunks
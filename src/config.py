DOC_ID = "doc01"
PDF_PATH = "data/raw/doc01.pdf"
MANIFEST = "data/manifest.json"
BENCHMARK = "benchmark/questions.json"
CHROMA_PATH = "vectorstore/chroma"

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

A_SIZE, A_OVERLAP = 500, 50
B_MAX, B_MIN = 1000, 200

COLLECTIONS = {"A": "chunks_A", "B": "chunks_B"}  # C dùng lại collection của B
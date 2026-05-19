import fitz  # PyMuPDF


CHUNK_SIZE = 500      # words
CHUNK_OVERLAP = 50    # words


def chunk_pdf(pdf_path: str) -> list[str]:
    """Extract text from PDF and split into overlapping word-based chunks."""
    text = _extract_text(pdf_path)
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        chunk_words = words[i: i + CHUNK_SIZE]
        chunk = " ".join(chunk_words)
        if chunk.strip():
            chunks.append(chunk)
        i += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def _extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    return " ".join(pages)
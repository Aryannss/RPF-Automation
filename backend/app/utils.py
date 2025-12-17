import os
import uuid
from pdfminer.high_level import extract_text

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_upload(file_bytes: bytes, filename: str) -> str:
    rfp_id = str(uuid.uuid4())
    path = os.path.join(UPLOAD_DIR, f"{rfp_id}__{filename}")
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path, rfp_id

def extract_text_from_pdf(path: str) -> str:
    # for prototype: use pdfminer to extract text from PDF, fallback to reading txt
    if path.lower().endswith(".pdf"):
        return extract_text(path)
    else:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

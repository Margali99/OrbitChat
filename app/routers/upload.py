import io
import uuid
from pypdf import PdfReader
import docx
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.deps import get_session_id
from app.db.store import db_save_document

router = APIRouter()

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()
    elif ext == "docx":
        doc = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join([p.text for p in doc.paragraphs])
        return text.strip()
    elif ext in ["txt", "md", "csv", "json"]:
        return file_bytes.decode("utf-8", errors="replace").strip()
    else:
        raise ValueError(f"Unsupported file format: .{ext}")

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Depends(get_session_id)
):
    contents = await file.read()
    try:
        extracted = extract_text_from_file(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

    doc_id = str(uuid.uuid4())
    db_save_document(doc_id, session_id, file.filename, extracted)

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "text_length": len(extracted)
    }

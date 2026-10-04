from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..config import settings
from ..database import get_db
from ..models import Document, User
from ..services.rag import ingest

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def list_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.scalars(select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc())).all()
    return [{"id": d.id, "filename": d.filename, "document_type": d.document_type, "created_at": d.created_at.isoformat()} for d in docs]


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".csv", ".txt", ".md"}:
        return {"error": "Supported formats: PDF, CSV, TXT, MD"}
    safe_name = f"{uuid.uuid4().hex}{suffix}"
    target = Path(settings.upload_dir) / safe_name
    target.write_bytes(await file.read())
    doc = Document(user_id=user.id, filename=file.filename or safe_name, document_type=suffix[1:], stored_path=str(target))
    db.add(doc)
    db.commit()
    db.refresh(doc)
    try:
        chunks = ingest(target, user.id, doc.id)
    except Exception as exc:
        chunks = 0
        return {"id": doc.id, "filename": doc.filename, "chunks": chunks, "warning": str(exc)}
    return {"id": doc.id, "filename": doc.filename, "chunks": chunks}

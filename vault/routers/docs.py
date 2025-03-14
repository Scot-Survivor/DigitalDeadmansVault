from typing import Optional
from fastapi import APIRouter, Request
from sqlmodel import Session
from fastapi_pagination import Page, paginate
from vault.util import save_a_file
from vault.config import get_main_config
from vault.models.docs import Document
from vault.models.util import Checksum
from vault.dependencies import HMACAuthDepends, SessionDepends

config = get_main_config()


router = APIRouter(
    prefix="/docs", tags=["docs"], responses={404: {"description": "Not found"}}, dependencies=[HMACAuthDepends]
)


@router.get("/{doc_id}", response_model=Optional[Document])
async def get_doc(doc_id: str, session: Session = SessionDepends) -> Optional[Document]:
    """Get a document by its ID"""
    return session.get(Document, doc_id)


@router.post("/create", response_model=Document)
async def create_doc(request: Request, session: Session = SessionDepends) -> Document:
    """Creates a document and saves it to file system"""
    # get file from stream
    form = await request.form()
    file = form["file"]
    file_content = await file.read()

    file_path = await save_a_file(file_content, file.filename)
    checksums = [(algo.hash(file_content.decode()), algo) for algo in config.checksum_algorithms]

    doc = Document(fs_path=file_path)
    session.add(doc)
    session.commit()

    # Create checksums
    for checksum, algo in checksums:
        obj = Checksum(document_id=doc.id, value=checksum, algorithm=str(algo))
        session.add(obj)
    session.commit()

    return doc


@router.get("/list", response_model=Page[Document.id])
async def list_docs(session: Session = SessionDepends) -> Page[Document.id]:
    """Get a paginated list of document IDs"""
    document_ids = Document.select(Document.id).order_by(Document)
    return paginate(session, document_ids)

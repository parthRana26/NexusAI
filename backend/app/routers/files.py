from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.controllers.file_controller import FileController
from app.schemas.file import FileAskRequest

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form("general"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await FileController.upload_file(db, current_user, file, category)

@router.get("/list")
def list_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return FileController.list_files(db, current_user)

@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return FileController.delete_file(db, current_user, file_id)

@router.post("/query")
def query_documents(
    request: FileAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return FileController.ask_document_question(db, current_user, request.question, file_id=request.file_id)

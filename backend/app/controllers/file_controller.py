from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.models.user import User
from app.services.file_service import FileService

class FileController:
    @staticmethod
    async def upload_file(db: Session, current_user: User, file: UploadFile, category: str):
        return await FileService.upload_file(db, current_user.id, file, category)

    @staticmethod
    def list_files(db: Session, current_user: User):
        return FileService.get_user_files(db, current_user.id)

    @staticmethod
    def delete_file(db: Session, current_user: User, file_id: int):
        success = FileService.delete_file(db, current_user.id, file_id)
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        return {"message": "File deleted successfully"}

    @staticmethod
    def ask_document_question(db: Session, current_user: User, question: str, file_id: int = None):
        return FileService.ask_question(current_user.id, question, file_id=file_id, db=db)

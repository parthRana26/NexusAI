from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.memory import UserMemory

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.post("/save")
def save_memory(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    text = payload.get("content")

    if not text:
        raise HTTPException(status_code=400, detail="content required")

    item = UserMemory(
        user_id=current_user.id,
        content=text
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {"message": "Memory saved", "id": item.id}


@router.get("/list")
def list_memory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = db.query(UserMemory).filter(
        UserMemory.user_id == current_user.id
    ).order_by(UserMemory.id.desc()).all()

    return rows


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    row = db.query(UserMemory).filter(
        UserMemory.id == memory_id,
        UserMemory.user_id == current_user.id
    ).first()

    if not row:
        raise HTTPException(status_code=404, detail="Memory not found")

    db.delete(row)
    db.commit()

    return {"message": "Memory deleted"}
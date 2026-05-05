from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from jose import jwt, JWTError

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)
from app.core.config import settings

class AuthController:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate):
        existing = db.query(User).filter(User.email == user_in.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        new_user = User(
            full_name=user_in.full_name,
            email=user_in.email,
            hashed_password=hash_password(user_in.password),
            role="user"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Registered successfully", "user_id": new_user.id}

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        return {
            "access_token": create_access_token({"user_id": user.id}),
            "refresh_token": create_refresh_token({"user_id": user.id}),
            "token_type": "bearer"
        }

    @staticmethod
    def refresh_access_token(refresh_token: str):
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )

            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token payload"
                )

            return {
                "access_token": create_access_token({"user_id": user_id}),
                "token_type": "bearer"
            }

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate refresh token"
            )

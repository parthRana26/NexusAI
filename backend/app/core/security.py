from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("user_id")
        token_type = payload.get("type")

        if token_type != "access":
            from app.core.logging import logger
            logger.warning(f"Invalid token type: {token_type}")
            raise HTTPException(401, "Invalid token type")

        if user_id is None:
            from app.core.logging import logger
            logger.warning("JWT payload missing user_id")
            raise HTTPException(401, "Invalid token")

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            from app.core.logging import logger
            logger.warning(f"User with ID {user_id} not found in database")
            raise HTTPException(401, "User not found")

        return user

    except JWTError as e:
        from app.core.logging import logger
        logger.error(f"JWT Decode Error: {e}")
        raise HTTPException(401, "Invalid token")


def require_admin(current_user: User = Depends(get_current_user)):
    # Normalize role check to be case-insensitive
    if current_user.role.lower() != "admin":
        from app.core.logging import logger
        logger.warning(f"Permission Denied: User {current_user.email} (role: {current_user.role}) attempted admin access")
        raise HTTPException(403, "Admin access required")
    return current_user
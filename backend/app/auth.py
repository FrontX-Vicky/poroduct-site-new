import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from . import models
from .config import SESSION_TTL_HOURS
from .database import get_db

SESSION_TTL = timedelta(hours=SESSION_TTL_HOURS)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    salt, digest = stored.split("$", 1)
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return hmac.compare_digest(check, digest)


def create_session(db: DbSession, user: models.User) -> str:
    token = secrets.token_hex(32)
    db.add(models.Session(token=token, user_id=user.id, expires_at=datetime.now() + SESSION_TTL))
    db.commit()
    return token


def get_current_session(
    authorization: str | None = Header(default=None),
    db: DbSession = Depends(get_db),
) -> models.Session:
    """Reject the request unless it carries a valid, unexpired session token."""
    unauthorized = HTTPException(status.HTTP_401_UNAUTHORIZED, "Not logged in or session expired")
    if not authorization or not authorization.startswith("Bearer "):
        raise unauthorized
    session = db.get(models.Session, authorization.removeprefix("Bearer "))
    if session is None:
        raise unauthorized
    if session.expires_at < datetime.now():
        db.delete(session)
        db.commit()
        raise unauthorized
    return session


def get_current_user(session: models.Session = Depends(get_current_session)) -> models.User:
    return session.user

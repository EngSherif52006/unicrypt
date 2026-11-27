from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from itsdangerous import BadSignature, URLSafeTimedSerializer
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .models import User

password_hasher = PasswordHasher()
signer = URLSafeTimedSerializer(settings.secret_key, salt="unicrypt-session")
SESSION_COOKIE = "unicrypt_session"


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False


def set_session(response, user_id: int) -> None:
    token = signer.dumps({"user_id": user_id})
    response.set_cookie(
        SESSION_COOKIE, token, max_age=60 * 60 * 24 * 7, httponly=True,
        secure=settings.cookie_secure, samesite=settings.cookie_samesite, path="/"
    )


def clear_session(response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/")


def get_current_user(request: Request, db: Session) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="تسجيل الدخول مطلوب")
    try:
        payload = signer.loads(token, max_age=60 * 60 * 24 * 7)
        user = db.get(User, int(payload["user_id"]))
    except (BadSignature, KeyError, ValueError, TypeError):
        user = None
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="جلسة غير صالحة")
    return user


def require_role(*roles: str):
    def dependency(request: Request, db: Annotated[Session, Depends(get_db)]) -> User:
        user = get_current_user(request, db)
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="لا تملك صلاحية هذه العملية")
        return user
    return dependency


def current_user_dependency(request: Request, db: Annotated[Session, Depends(get_db)]) -> User:
    return get_current_user(request, db)


CurrentUser = Annotated[User, Depends(current_user_dependency)]

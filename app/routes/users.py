from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from ..authentication import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import UserOut, UserUpdate

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(request: Request, q: str = Query(default="", max_length=80), role: str | None = None, db: Session = Depends(get_db)):
    get_current_user(request, db)
    statement = select(User).where(User.username != "")
    if q:
        pattern = f"%{q}%"
        statement = statement.where(or_(User.username.ilike(pattern), User.department.ilike(pattern)))
    if role in {"student", "professor"}:
        statement = statement.where(User.role == role)
    return list(db.scalars(statement.order_by(User.username)).all())


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    get_current_user(request, db)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "المستخدم غير موجود")
    return user


@router.patch("/me", response_model=UserOut)
def update_me(payload: UserUpdate, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    user.department = payload.department
    user.profile_image = payload.profile_image
    db.commit(); db.refresh(user)
    return user

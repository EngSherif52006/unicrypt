from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..authentication import clear_session, get_current_user, hash_password, set_session, verify_password
from ..database import get_db
from ..models import User
from ..schemas import LoginInput, UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.username == payload.username)):
        raise HTTPException(409, "اسم المستخدم مستخدم بالفعل")
    user = User(username=payload.username, password_hash=hash_password(payload.password), role=payload.role, department=payload.department)
    db.add(user); db.commit(); db.refresh(user)
    set_session(response, user.id)
    return user


@router.post("/login", response_model=UserOut)
def login(payload: LoginInput, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "اسم المستخدم أو كلمة المرور غير صحيحة")
    user.is_online = True; db.commit()
    set_session(response, user.id)
    return user


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    try:
        user = get_current_user(request, db)
        user.is_online = False; db.commit()
    except HTTPException:
        pass
    clear_session(response)
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(request: Request, db: Session = Depends(get_db)):
    return get_current_user(request, db)

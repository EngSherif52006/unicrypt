from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from .config import settings
from .database import Base, SessionLocal, engine
from .models import User
from .authentication import hash_password, get_current_user
from .websocket_manager import manager
from .routes import auth, users, conversations, messages, encryption, voice


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    try:
        if not db.scalar(select(User).where(User.username == "demo_student")):
            db.add_all([
                User(username="demo_student", password_hash=hash_password("Student@123"), role="student", department="Computer Science"),
                User(username="demo_professor", password_hash=hash_password("Professor@123"), role="professor", department="Information Security"),
            ])
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(encryption.router)
app.include_router(voice.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "unicrypt", "environment": settings.environment}


@app.get("/manus-routes.json")
def route_manifest():
    return {"routes": [
        {"path": "/", "title": "UniCrypt"}, {"path": "/login", "title": "تسجيل الدخول"},
        {"path": "/register", "title": "إنشاء حساب"}, {"path": "/dashboard", "title": "لوحة التحكم"},
        {"path": "/student", "title": "لوحة الطالب"}, {"path": "/professor", "title": "لوحة الأستاذ"},
        {"path": "/chat", "title": "المحادثة الخاصة"}, {"path": "/lab", "title": "معمل التشفير"},
        {"path": "/comparison", "title": "مقارنة الخوارزميات"}, {"path": "/profile", "title": "الملف الشخصي"},
        {"path": "/security", "title": "معلومات الأمان"}, {"path": "/voice", "title": "الرسائل الصوتية"},
    ]}


@app.get("/{path:path}", response_class=HTMLResponse)
def frontend(request: Request, path: str = ""):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    db = SessionLocal()
    try:
        try:
            user = get_current_user(websocket, db)
        except Exception:
            await websocket.close(code=4401)
            return
        if user.id != user_id:
            await websocket.close(code=4403)
            return
        await manager.connect(user_id, websocket)
        user.is_online = True; db.commit()
        await websocket.send_json({"type": "presence", "status": "online", "user_id": user_id})
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
        user = db.get(User, user_id)
        if user:
            user.is_online = False; db.commit()
    finally:
        db.close()

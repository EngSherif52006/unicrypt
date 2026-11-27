import base64
import secrets
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from ..authentication import get_current_user
from ..config import settings
from ..database import get_db
from ..encryption.aes import derive_key
from ..models import Conversation, VoiceMessage
from .conversations import can_access
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/upload")
async def upload_voice(conversation_id: int, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    conversation = db.get(Conversation, conversation_id)
    if not conversation or not can_access(conversation, user.id):
        raise HTTPException(404, "المحادثة غير موجودة")
    content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, "الملف أكبر من الحجم المسموح")
    nonce = secrets.token_bytes(12)
    encrypted = AESGCM(derive_key(f"{settings.secret_key}:conversation:{conversation_id}" )).encrypt(nonce, content, None)
    filename = f"voice_{secrets.token_urlsafe(16)}.bin"
    path = Path(settings.upload_dir); path.mkdir(parents=True, exist_ok=True)
    (path / filename).write_bytes(encrypted)
    record = VoiceMessage(conversation_id=conversation_id, sender_id=user.id, encrypted_file_path=filename, nonce=base64.urlsafe_b64encode(nonce).decode())
    db.add(record); db.commit(); db.refresh(record)
    return {"id": record.id, "filename": filename, "created_at": record.created_at.isoformat(), "notice": "تسجيل صوتي حقيقي مشفر AES-GCM"}


@router.get("/{voice_id}")
async def get_voice(voice_id: int, request: Request, db: Session = Depends(get_db)):
    from fastapi.responses import Response
    user = get_current_user(request, db)
    record = db.get(VoiceMessage, voice_id)
    if not record:
        raise HTTPException(404, "التسجيل غير موجود")
    conversation = db.get(Conversation, record.conversation_id)
    if not conversation or not can_access(conversation, user.id):
        raise HTTPException(403, "غير مصرح")
    encrypted = (Path(settings.upload_dir) / record.encrypted_file_path).read_bytes()
    plaintext = AESGCM(derive_key(f"{settings.secret_key}:conversation:{record.conversation_id}" )).decrypt(base64.urlsafe_b64decode(record.nonce), encrypted, None)
    return Response(content=plaintext, media_type="audio/webm", headers={"X-Voice-Authenticity": "recorded-audio; no voice cloning"})

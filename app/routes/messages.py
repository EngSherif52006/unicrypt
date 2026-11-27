from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..authentication import get_current_user
from ..config import settings
from ..database import get_db
from ..encryption.aes import decrypt as aes_decrypt, encrypt as aes_encrypt
from ..models import Conversation, Message, User
from ..schemas import MessageCreate
from ..websocket_manager import manager
from .conversations import can_access

router = APIRouter(prefix="/api/messages", tags=["messages"])


def conversation_key(conversation_id: int) -> str:
    return f"{settings.secret_key}:conversation:{conversation_id}"


def serialize(message: Message, key: str | None = None):
    data = {"id": message.id, "conversation_id": message.conversation_id, "sender_id": message.sender_id, "algorithm": message.algorithm, "message_type": message.message_type, "delivery_status": message.delivery_status, "created_at": message.created_at.isoformat()}
    if key:
        try:
            data["content"] = aes_decrypt(message.encrypted_content, key, message.nonce, message.authentication_tag)
        except Exception:
            data["content"] = "تعذر التحقق من سلامة الرسالة"
    return data


@router.get("/{conversation_id}")
def list_messages(conversation_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    conversation = db.get(Conversation, conversation_id)
    if not conversation or not can_access(conversation, user.id):
        raise HTTPException(404, "المحادثة غير موجودة")
    key = conversation_key(conversation_id)
    return [serialize(m, key) for m in db.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)).all()]


@router.post("")
async def create_message(payload: MessageCreate, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    conversation = db.get(Conversation, payload.conversation_id)
    if not conversation or not can_access(conversation, user.id):
        raise HTTPException(404, "المحادثة غير موجودة")
    encrypted = aes_encrypt(payload.content, conversation_key(conversation.id))
    message = Message(conversation_id=conversation.id, sender_id=user.id, encrypted_content=encrypted["ciphertext"], nonce=encrypted["nonce"], authentication_tag=encrypted["tag"])
    db.add(message); db.commit(); db.refresh(message)
    recipient_id = conversation.professor_id if user.id == conversation.student_id else conversation.student_id
    message.delivery_status = "delivered" if manager.is_online(recipient_id) else "sent"
    db.commit()
    payload_out = serialize(message, conversation_key(conversation.id))
    await manager.send_user(recipient_id, {"type": "message", "message": payload_out})
    return payload_out

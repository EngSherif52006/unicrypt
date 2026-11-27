from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from ..authentication import get_current_user
from ..database import get_db
from ..models import Conversation, User
from ..schemas import ConversationCreate, ConversationOut

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


def can_access(conversation: Conversation, user_id: int) -> bool:
    return user_id in {conversation.student_id, conversation.professor_id}


@router.get("", response_model=list[ConversationOut])
def list_conversations(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return list(db.scalars(select(Conversation).where(or_(Conversation.student_id == user.id, Conversation.professor_id == user.id)).order_by(Conversation.created_at.desc())).all())


@router.post("", response_model=ConversationOut)
def create_conversation(payload: ConversationCreate, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    peer = db.get(User, payload.peer_id)
    if not peer or peer.id == user.id:
        raise HTTPException(400, "المستخدم المطلوب غير صالح")
    student_id, professor_id = (user.id, peer.id) if user.role == "student" and peer.role == "professor" else (peer.id, user.id) if user.role == "professor" and peer.role == "student" else (user.id, peer.id)
    existing = db.scalar(select(Conversation).where(Conversation.student_id == student_id, Conversation.professor_id == professor_id))
    if existing:
        return existing
    conversation = Conversation(student_id=student_id, professor_id=professor_id)
    db.add(conversation); db.commit(); db.refresh(conversation)
    return conversation


@router.get("/{conversation_id}", response_model=ConversationOut)
def get_conversation(conversation_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    conversation = db.get(Conversation, conversation_id)
    if not conversation or not can_access(conversation, user.id):
        raise HTTPException(404, "المحادثة غير موجودة")
    return conversation

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80, pattern=r"^[\w\-.]+$")
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(pattern="^(student|professor)$")
    department: str = Field(default="", max_length=120)


class LoginInput(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    department: str = Field(default="", max_length=120)
    profile_image: str | None = Field(default=None, max_length=500)


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    department: str
    profile_image: str | None
    is_online: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationCreate(BaseModel):
    peer_id: int


class ConversationOut(BaseModel):
    id: int
    student_id: int
    professor_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    conversation_id: int
    content: str = Field(min_length=1, max_length=4000)


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    encrypted_content: str
    nonce: str
    authentication_tag: str
    algorithm: str
    message_type: str
    delivery_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EncryptRequest(BaseModel):
    algorithm: str
    plaintext: str = Field(max_length=10000)
    key: str = Field(min_length=1, max_length=256)
    decrypt_ciphertext: str | None = None


class DecryptRequest(BaseModel):
    algorithm: str
    ciphertext: str
    key: str = Field(min_length=1, max_length=256)
    nonce: str | None = None
    tag: str | None = None

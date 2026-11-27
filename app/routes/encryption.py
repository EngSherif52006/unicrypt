from fastapi import APIRouter, Depends, HTTPException, Request
from ..authentication import get_current_user
from ..database import get_db
from ..encryption.service import ALGORITHMS, decrypt, encrypt
from ..schemas import DecryptRequest, EncryptRequest

router = APIRouter(prefix="/api/encryption", tags=["encryption"])


@router.get("/algorithms")
def algorithms(request: Request, db=Depends(get_db)):
    get_current_user(request, db)
    return [{"id": key, "label": value["label"], "kind": value["kind"], "warning": value["warning"]} for key, value in ALGORITHMS.items()]


@router.post("/encrypt")
def encrypt_route(payload: EncryptRequest, request: Request, db=Depends(get_db)):
    get_current_user(request, db)
    try:
        result = encrypt(payload.algorithm, payload.plaintext, payload.key)
        result["ciphertext_size"] = len(result["ciphertext"])
        return result
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc


@router.post("/decrypt")
def decrypt_route(payload: DecryptRequest, request: Request, db=Depends(get_db)):
    get_current_user(request, db)
    try:
        return decrypt(payload.algorithm, payload.ciphertext, payload.key, payload.nonce, payload.tag)
    except Exception as exc:
        raise HTTPException(400, f"فشل فك التشفير أو التحقق من السلامة: {exc}") from exc

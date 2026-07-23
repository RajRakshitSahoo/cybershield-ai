from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, status

from app.auth.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.auth.dependencies import require_user
from app.database import get_db
from app.models.schemas import RegisterRequest, LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest):
    db = get_db()
    existing = await db["users"].find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    is_first_user = await db["users"].count_documents({}) == 0
    user_doc = {
        "name": payload.name,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "role": "admin" if is_first_user else "user",
        "created_at": datetime.now(timezone.utc),
    }
    await db["users"].insert_one(user_doc)
    access = create_access_token({"sub": payload.email})
    refresh = create_refresh_token({"sub": payload.email})
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    db = get_db()
    user = await db["users"].find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access = create_access_token({"sub": payload.email})
    refresh = create_refresh_token({"sub": payload.email})
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access = create_access_token({"sub": payload["sub"]})
    new_refresh = create_refresh_token({"sub": payload["sub"]})
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.get("/me", response_model=UserOut)
async def me(user=Depends(require_user)):
    return UserOut(name=user["name"], email=user["email"], role=user["role"], created_at=user["created_at"])

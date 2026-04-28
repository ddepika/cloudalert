from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import secrets
import hashlib
from app.database import get_db
from app.models.user import User
from app.utils.email_service import send_verification_email, send_alert_email

router = APIRouter()

FRONTEND_URL = "http://localhost:5173"

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AlertRequest(BaseModel):
    email: EmailStr
    name: str
    district: str
    risk_level: str
    probability: float

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

@router.post("/register")
async def register_user(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    print(f"Registering user: {user_data.email}")

    existing_user = db.query(User).filter(func.lower(User.email) == func.lower(user_data.email)).first()

    if existing_user:
        if existing_user.is_verified:
            raise HTTPException(status_code=400, detail="Email already registered and verified")
        else:
            verification_token = secrets.token_urlsafe(32)
            token_expiry = datetime.now() + timedelta(days=30)
            existing_user.verification_token = verification_token
            existing_user.token_expiry = token_expiry
            db.commit()

            await send_verification_email(
                existing_user.email,
                existing_user.name,
                verification_token,
                background_tasks
            )

            return {
                "success": True,
                "message": "Verification email resent. Please check your inbox.",
                "email": existing_user.email
            }

    verification_token = secrets.token_urlsafe(32)
    token_expiry = datetime.now() + timedelta(days=30)

    new_user = User(
        name=user_data.name,
        email=user_data.email.lower(),
        password_hash=hash_password(user_data.password),
        is_verified=False,
        verification_token=verification_token,
        token_expiry=token_expiry
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    await send_verification_email(
        user_data.email,
        user_data.name,
        verification_token,
        background_tasks
    )

    return {
        "success": True,
        "message": "Registration successful. Please check your email for verification link.",
        "email": user_data.email
    }

@router.post("/login")
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    print(f"Login attempt: {login_data.email}")

    user = db.query(User).filter(func.lower(User.email) == func.lower(login_data.email)).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_verified:
        return {
            "success": False,
            "verified": False,
            "message": "Please verify your email first. Check your inbox for verification link.",
            "email": user.email
        }

    user.last_login = datetime.now()
    db.commit()

    return {
        "success": True,
        "verified": True,
        "id": user.id,
        "name": user.name,
        "email": user.email
    }

@router.get("/verify/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    print(f"Verifying token: {token[:20]}...")

    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        print(f"No user found with token")
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=invalid_token")

    print(f"Found user: {user.email}, Verified: {user.is_verified}")

    if user.is_verified:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?verified=true")

    if user.token_expiry and user.token_expiry < datetime.now():
        print(f"Token expired for: {user.email}")
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=token_expired")

    user.is_verified = True
    user.verification_token = None
    user.token_expiry = None
    db.commit()

    print(f"User {user.email} verified successfully")

    return RedirectResponse(url=f"{FRONTEND_URL}/login?verified=true")

@router.get("/check-verification")
async def check_verification(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == func.lower(email)).first()

    if not user:
        return {"verified": False, "message": "User not found"}

    return {"verified": user.is_verified, "name": user.name, "email": user.email}

@router.post("/resend-verification")
async def resend_verification(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    print(f"Resending verification for: {email}")

    user = db.query(User).filter(func.lower(User.email) == func.lower(email)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    new_token = secrets.token_urlsafe(32)
    new_expiry = datetime.now() + timedelta(days=30)
    user.verification_token = new_token
    user.token_expiry = new_expiry
    db.commit()

    await send_verification_email(
        user.email,
        user.name,
        new_token,
        background_tasks
    )

    return {"message": "Verification email resent. Please check your inbox."}

@router.post("/send-alert")
async def send_alert(alert: AlertRequest, background_tasks: BackgroundTasks):
    await send_alert_email(
        alert.email,
        alert.name,
        alert.district,
        alert.risk_level,
        alert.probability,
        background_tasks
    )

    return {
        "message": "Alert sent successfully",
        "sent_to": alert.email
    }

@router.get("/test")
async def test_auth():
    return {"message": "Auth router is working"}

@router.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "is_verified": u.is_verified,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]

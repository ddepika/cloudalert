from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import hashlib
from app.database import get_db
from app.models.user import User

router = APIRouter()

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
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    print(f"Registering user: {user_data.email}")
    
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        return {
            "success": False,
            "message": "User already exists. Please login."
        }
    
    verification_token = secrets.token_urlsafe(32)
    token_expiry = datetime.now() + timedelta(days=30)
    
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        is_verified=False,
        verification_token=verification_token,
        token_expiry=token_expiry
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    verification_link = f"http://localhost:8000/api/auth/verify/{verification_token}"
    print(f"\n{'='*60}")
    print(f"VERIFICATION LINK for {user_data.email}")
    print(f"Valid until: {token_expiry.strftime('%Y-%m-%d %H:%M:%S')}")
    print(verification_link)
    print(f"{'='*60}\n")
    
    return {
        "success": True,
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "is_verified": False,
        "message": "Registration successful! Please verify your email."
    }

@router.post("/login")
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    print(f"Login attempt: {login_data.email}")
    
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user.last_login = datetime.now()
    db.commit()
    
    return {
        "success": True,
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_verified": user.is_verified,
        "message": "Login successful"
    }

@router.get("/verify/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Invalid verification token")
    
    if user.is_verified:
        return {"message": "Email already verified", "redirect": "http://localhost:3000"}
    
    if user.token_expiry and user.token_expiry < datetime.now():
        new_token = secrets.token_urlsafe(32)
        new_expiry = datetime.now() + timedelta(days=30)
        user.verification_token = new_token
        user.token_expiry = new_expiry
        db.commit()
        return {"message": "Token expired! New verification link generated. Check console."}
    
    user.is_verified = True
    user.verification_token = None
    user.token_expiry = None
    db.commit()
    
    print(f"User {user.email} verified successfully!")
    return {"message": "Email verified successfully!", "redirect": "http://localhost:3000"}

@router.get("/check-verification")
async def check_verification(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return {"verified": False, "message": "User not found"}
    
    return {"verified": user.is_verified, "name": user.name}

@router.post("/resend-verification")
async def resend_verification(email: EmailStr, db: Session = Depends(get_db)):
    print(f"Resending verification for: {email}")
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    new_token = secrets.token_urlsafe(32)
    new_expiry = datetime.now() + timedelta(days=30)
    user.verification_token = new_token
    user.token_expiry = new_expiry
    db.commit()
    
    verification_link = f"http://localhost:8000/api/auth/verify/{new_token}"
    print(f"\n{'='*60}")
    print(f"RESENT VERIFICATION LINK for {email}")
    print(f"Valid until: {new_expiry.strftime('%Y-%m-%d %H:%M:%S')}")
    print(verification_link)
    print(f"{'='*60}\n")
    
    return {"message": "Verification email resent. Check console for the link."}

@router.get("/test")
async def test_auth():
    return {"message": "Auth router is working!"}

@router.post("/send-alert")
async def send_alert(alert: AlertRequest, background_tasks: BackgroundTasks):
    print(f"\n{'='*60}")
    print(f"ALERT REQUEST")
    print(f"  To: {alert.email}")
    print(f"  Name: {alert.name}")
    print(f"  District: {alert.district}")
    print(f"  Risk Level: {alert.risk_level}")
    print(f"  Probability: {alert.probability}%")
    print(f"{'='*60}\n")
    
    return {
        "message": "Alert sent successfully",
        "sent_to": alert.email,
        "district": alert.district,
        "risk_level": alert.risk_level
    }

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

"""
Authentication module for AIE Map admin functions
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import logging

from models import AdminSession

# Load environment variables
load_dotenv()

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBasic()

# Get configuration from environment
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "change-this-default-key")
SESSION_EXPIRE_HOURS = int(os.getenv("SESSION_EXPIRE_HOURS", "24"))
SESSION_COOKIE_NAME = "aie_map_admin_session"

# Rate limiting for login attempts
login_attempts = {}
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
LOGIN_COOLDOWN_MINUTES = int(os.getenv("LOGIN_COOLDOWN_MINUTES", "15"))

logger = logging.getLogger(__name__)

def verify_password(plain_password: str) -> bool:
    """Verify password against stored hash"""
    if not ADMIN_PASSWORD_HASH:
        logger.error("ADMIN_PASSWORD_HASH not set in environment")
        return False
    try:
        return pwd_context.verify(plain_password, ADMIN_PASSWORD_HASH)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def check_rate_limit(ip_address: str) -> bool:
    """Check if IP is rate limited"""
    now = datetime.utcnow()
    
    # Clean old entries
    for ip in list(login_attempts.keys()):
        if login_attempts[ip]["reset_time"] < now:
            del login_attempts[ip]
    
    if ip_address in login_attempts:
        attempt_data = login_attempts[ip_address]
        if attempt_data["attempts"] >= MAX_LOGIN_ATTEMPTS:
            if attempt_data["reset_time"] > now:
                return False
    
    return True

def record_login_attempt(ip_address: str, success: bool):
    """Record login attempt for rate limiting"""
    now = datetime.utcnow()
    
    if success:
        # Clear attempts on successful login
        if ip_address in login_attempts:
            del login_attempts[ip_address]
        return
    
    if ip_address not in login_attempts:
        login_attempts[ip_address] = {
            "attempts": 0,
            "reset_time": now + timedelta(minutes=LOGIN_COOLDOWN_MINUTES)
        }
    
    login_attempts[ip_address]["attempts"] += 1

def create_session(db: Session, ip_address: str) -> str:
    """Create a new admin session"""
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=SESSION_EXPIRE_HOURS)
    
    session = AdminSession(
        id=session_id,
        expires_at=expires_at,
        ip_address=ip_address
    )
    
    db.add(session)
    db.commit()
    
    return session_id

def get_session(db: Session, session_id: str) -> Optional[AdminSession]:
    """Get a valid session"""
    if not session_id:
        return None
        
    session = db.query(AdminSession).filter(
        AdminSession.id == session_id,
        AdminSession.expires_at > datetime.utcnow()
    ).first()
    
    if session:
        # Update last accessed time
        session.last_accessed = datetime.utcnow()
        db.commit()
    
    return session

def delete_session(db: Session, session_id: str):
    """Delete a session (logout)"""
    db.query(AdminSession).filter(AdminSession.id == session_id).delete()
    db.commit()

def clean_expired_sessions(db: Session):
    """Clean up expired sessions"""
    db.query(AdminSession).filter(
        AdminSession.expires_at < datetime.utcnow()
    ).delete()
    db.commit()

def get_client_ip(request: Request) -> str:
    """Get client IP address, considering proxies"""
    # Check X-Forwarded-For header first (for proxies/load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct connection IP
    return request.client.host
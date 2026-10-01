# Authentication (JWT) + Role-Based Access Control (RBAC) middleware/dependencies
import hashlib, os, datetime as dt, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from models import User

SECRET = os.getenv("SECRET_KEY", "dev-secret-change-me")
bearer = OAuth2PasswordBearer(tokenUrl="/api/login")

def hash_pw(p):
    return hashlib.pbkdf2_hmac("sha256", p.encode(), b"mams-salt", 100_000).hex()

def create_token(user):
    exp = dt.datetime.utcnow() + dt.timedelta(hours=8)
    return jwt.encode({"sub": user.username, "exp": exp}, SECRET, algorithm="HS256")

def current_user(token: str = Depends(bearer), db=Depends(get_db)):
    try:
        name = jwt.decode(token, SECRET, algorithms=["HS256"])["sub"]
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token")
    user = db.query(User).filter(User.username == name).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user

def require(*roles):
    """RBAC: use as Depends(require('admin', ...)); rejects other roles with 403."""
    def check(user=Depends(current_user)):
        if user.role not in roles:
            raise HTTPException(403, f"Role '{user.role}' is not allowed here")
        return user
    return check

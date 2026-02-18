from fastapi import APIRouter, HTTPException, Depends
from datetime import timedelta
from jose import JWTError, jwt
from src.core.security.auth import (
    create_access_token, 
    verify_token,
    authenticate_user,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.core.models.user_model import User, Token, TokenData
from src.core.security.hash_utils import hash_password

router = APIRouter()

# Fake user database (replace with real DB in production)
fake_users_db = {
    "user1": User(
        user_id="user1",
        username="researcher1",
        email="researcher1@example.com",
        hashed_password=hash_password("password123"),
        full_name="Researcher One",
        is_active=True,
        is_admin=False,
        papers=["paper001", "paper002"]
    ),
    "admin": User(
        user_id="admin",
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("admin123"),
        full_name="System Admin",
        is_active=True,
        is_admin=True,
        papers=[]
    )
}

@router.post("/login", response_model=Token)
async def login(user_id: str, password: str):
    """
    User login to get access token
    """
    user = authenticate_user(fake_users_db, user_id, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect user ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(token: str = Depends(verify_token)):
    """
    Get current user info (requires valid token)
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = fake_users_db.get(token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return user

@router.post("/register")
async def register_user(
    user_id: str,
    username: str,
    email: str,
    password: str,
    full_name: str = ""
):
    """
    Register new user (simplified)
    """
    if user_id in fake_users_db:
        raise HTTPException(
            status_code=400,
            detail="User ID already exists"
        )
    
    # Create new user
    new_user = User(
        user_id=user_id,
        username=username,
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        is_active=True,
        is_admin=False,
        papers=[]
    )
    
    # Add to fake DB
    fake_users_db[user_id] = new_user
    
    return {
        "status": "success",
        "message": f"User {user_id} registered successfully",
        "user_id": user_id
    }
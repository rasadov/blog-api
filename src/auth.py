"""
Contains routes for user authentication and authorization.
"""
from fastapi import Depends, APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models import User
from src.schemas import UserRegisterSchema, UserLoginSchema
from utils import verify_password, hash_password
import oauth2


router = APIRouter(
    tags=["Authentication"]
)

@router.post('/register')
async def register(user: UserRegisterSchema, db: AsyncSession = Depends(get_db)):
    user_exists = await db.execute(select(User).filter(User.email == user.email))
    if user_exists.scalars().first():
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = oauth2.create_access_token(data={"user_id": new_user.id})
    response = JSONResponse(content={
        "user_id": new_user.id,
    })

    response.set_cookie("access_token", access_token)
    return response

@router.post("/login")
async def login(cred: UserLoginSchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == cred.email))
    user = result.scalars().first()

    if user is None or not verify_password(cred.password, user.password_hash):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    response = JSONResponse(content={
        "user_id": user.id,
    })

    response.set_cookie("access_token", access_token)

    return response

@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

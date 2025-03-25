# app/api/routes/auth.py
from fastapi import APIRouter, HTTPException, status, Body, Depends
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.utils import create_access_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.auth import Token  # Ensure Token schema includes a 'user' field
from app.models.user import User
from app.schemas.user import UserOut
from app.utils import verify_password
from app.core.database import get_db
from app.core.logger import logger

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(username: str = Body(...), password: str = Body(...), db: AsyncSession = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.
    Credentials are validated against the database.
    """
    logger.info(f"Login attempt: {username}")

    # Query the user from the database
    # query = await db.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username})
    # user = query.scalars().first()

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()


    if not user:
        logger.warning("User not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify the password
    if not verify_password(password, user.hashed_password):
        logger.warning("Incorrect password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token payload with user details (using user's id and name)
    user_data = {"id": user.id, "name": user.name, "username": user.username}
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=user_data, expires_delta=access_token_expires
    )
    logger.info(f"User {username} logged in successfully")

    return {"access_token": access_token, "token_type": "bearer", "user": user_data}
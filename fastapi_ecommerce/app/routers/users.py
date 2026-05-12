"""
User Router - MySQL Database Version
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session, get_async_session_with_commit
from app.managers.user_manager import UserManager
from app.models.schemas import UserCreate, UserUpdate, User, MessageResponse
from app.utils.loggers import logger

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session)
):
    logger.info(f"GET /users - skip={skip}, limit={limit}")
    try:
        return await UserManager.get_all_users(session=session, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch users")


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    user = await UserManager.get_user(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
    return user


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session_with_commit)
):
    logger.info(f"POST /users - Creating: {user_data.name}")
    try:
        return await UserManager.create_user(session=session, user_data=user_data)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_async_session_with_commit)
):
    try:
        updated = await UserManager.update_user(session=session, user_id=user_id, user_data=user_data)
        if not updated:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
        return updated
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session_with_commit)
):
    deleted = await UserManager.delete_user(session=session, user_id=user_id)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
    return MessageResponse(message=f"User {user_id} deleted successfully")